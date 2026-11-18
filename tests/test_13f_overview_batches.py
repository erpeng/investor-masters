"""Batch selection and instrument boundaries for the Q3 overview renderer."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_13f_institutions as u


def row(cusip='594918104', value=100, shares=10, option='', **extra):
    return dict(issuer='MICROSOFT CORP', cusip=cusip, security_class='COM',
                put_call=option, share_type='SH', value=value, shares=shares, **extra)


def snapshot(key, rows):
    filings=[]
    for i,date in enumerate(('2025-12-31','2026-03-31','2026-06-30','2026-09-30')):
        filings.append(dict(form='13F-HR',reportDate=date,filingDate='2026-11-16',
                            accessionNumber=f'fixture-{i}',url=f'https://www.sec.gov/fixture-{i}.txt',
                            rows=rows,cover_difference=0))
    return dict(institution=key,latest_quarter='2026Q3',as_of='2026-11-17',
                securities={r['cusip']:dict(ticker='MSFT',name=r['issuer']) for r in rows},
                filings=filings,splits=[],quotes={},
                editorial=dict(summary='本季事实。',method='方法。',notes=[]))


class BatchOverviewTest(unittest.TestCase):
    def test_warrant_and_new_adr_do_not_masquerade_as_common_shares(self):
        warrant=dict(row('G4124C117'),security_class='W EXP 12/1/202')
        self.assertEqual(u.category(warrant,'GRABW'),'权证')
        self.assertEqual(u.instrument_type(warrant),'权证')
        adr=dict(row('78392B206'),security_class='AMERICAN DEPOSIT')
        self.assertEqual(u.instrument_type(adr),'ADR/ADS')
        data=dict(securities={'78392B206':dict(ticker='SKHY',comparability_exclusion='new ADR listing')})
        self.assertEqual(u.category(adr,'SKHY',data),'不可比证券')

    def test_manifest_keeps_first_evidence_and_writes_only_new_institutions(self):
        manifest=Path(__file__).resolve().parents[1]/'scripts/data/13f-2026q3-batches.json'
        paths, institutions, horizontal=u.configure_manifest(manifest,Path('/vault'))
        self.assertEqual(institutions,tuple(u.g.BATCH4_MANAGERS))
        self.assertEqual(set(horizontal),set(u.g.ALL_MANAGERS))
        self.assertEqual(paths['berkshire'],Path('/vault/raw/data/13f-20261117/berkshire.json'))
        self.assertEqual(paths['pershing'],Path('/vault/raw/data/13f-20261117-batch2/pershing.json'))
        self.assertEqual(paths['akre'],Path('/vault/raw/data/13f-20261117-batch3/akre.json'))
        self.assertEqual(paths['tudor'],Path('/vault/raw/data/13f-20261117-batch4/tudor.json'))
        self.assertEqual([u.WEIGHTS[k] for k in institutions],[1.0,1.0,.9,1.1,1.1,1.0,1.0,.6])

    def test_default_cli_keeps_original_five_scope(self):
        periods=[dict(date=d) for d in ('2025-12-31','2026-03-31','2026-06-30','2026-09-30')]
        with mock.patch.object(sys,'argv',['update_13f_institutions.py','--only','institutions']), \
             mock.patch.object(u,'read',return_value=({},periods)), \
             mock.patch.object(u,'update_institution') as update, \
             mock.patch.object(u,'update_cross') as cross, \
             mock.patch.object(u,'SNAPSHOT_PATHS',{}), \
             mock.patch.object(u,'INSTITUTION_KEYS',u.FIRST_KEYS), \
             mock.patch.object(u,'CROSS_KEYS',u.FIRST_KEYS):
            u.main()
        self.assertEqual([call.args[0] for call in update.call_args_list],list(u.FIRST_KEYS))
        cross.assert_not_called()

    def test_special_and_unreliable_securities_never_score_as_ordinary(self):
        old=[row(),row('71531U102',500),row('fixture-unreliable',100),row('fixture-option',400,option='PUT')]
        new=[row(value=200,shares=20),row('71531U102',1000,shares=20),
             row('fixture-unreliable',1,value_reliable=False),row('fixture-option',500,option='PUT')]
        data=snapshot('pershing',old)
        data['filings'][-1]['rows']=new
        data['securities']['71531U102']['ticker']='PS'
        data['securities']['fixture-unreliable']['ticker']='BAD'
        data['securities']['fixture-option']['ticker']='QQQ'
        with mock.patch.object(u,'CROSS_KEYS',('pershing',)), \
             mock.patch.object(u,'read',return_value=(data,u.g.resolve_filings(data))):
            rows,_=u.cross_data()
        ordinary=[r for r in rows if r['category']=='普通股票']
        self.assertEqual([r['ticker'] for r in ordinary],['MSFT'])
        self.assertGreater(ordinary[0]['buy'],0)
        for r in rows:
            if r['ticker'] in ('PS','BAD'):
                self.assertEqual((r['buy'],r['sell'],r['active']),(0,0,0))

    def test_atreides_ordinary_table_uses_ordinary_denominator_preserves_background(self):
        rows=[row(value=100),row('fixture-option',900,option='PUT')]
        data=snapshot('atreides',rows)
        with tempfile.TemporaryDirectory() as directory:
            vault=Path(directory)
            target=vault/'wiki/institutions/Atreides Management.md'
            target.parent.mkdir(parents=True)
            target.write_text('---\nupdated: 2026-08-15\n---\n# Atreides Management\n\n'
                              '## 机构简介\n\n背景原样保留。\n\n## 13F 持仓（近五个季度）\n旧内容。\n'
                              '## 机构传承\n\n尾部原样保留。\n')
            with mock.patch.object(u,'VAULT',vault), \
                 mock.patch.object(u,'read',return_value=(data,u.g.resolve_filings(data))), \
                 contextlib.redirect_stdout(io.StringIO()):
                u.update_institution('atreides')
            text=target.read_text()
        self.assertIn('背景原样保留。',text)
        self.assertIn('尾部原样保留。',text)
        self.assertIn('非期权切片占比',text)
        self.assertIn('| 100.00% |',text)
        self.assertNotIn('| 10.00% |',text)
        self.assertIn('#### Q4 2025',text)
        self.assertNotIn('#### Q3 2025',text)

    def test_atreides_option_weight_does_not_borrow_ordinary_denominator(self):
        data=snapshot('atreides',[row(value=100),row('fixture-option',900,option='PUT')])
        data['securities']['fixture-option']['ticker']='QQQ'
        with mock.patch.object(u,'CROSS_KEYS',('atreides',)), \
             mock.patch.object(u,'read',return_value=(data,u.g.resolve_filings(data))):
            rows,_=u.cross_data()
        ordinary=next(x for x in rows if x['ticker']=='MSFT')
        option=next(x for x in rows if x['ticker']=='QQQ')
        self.assertEqual(ordinary['managers'][0]['w1'],100)
        self.assertEqual(option['managers'][0]['w1'],90)

    def test_cross_quote_uses_verified_currency_freshness_and_price_filter(self):
        r=row(value=100,shares=10)
        d=snapshot('fundsmith',[r])
        d['quotes']={'MSFT':dict(price=16,currency='USD',price_date='2026-11-16',source='https://quote.example/MSFT')}
        item=dict(category='普通股票',buyers=[dict(data=d,new=dict(rows=[(('key',),r)]))])
        self.assertIn('仅复盘/等待',u.quote_note(item))
        d['quotes']['MSFT']['price_date']='2026-10-01'
        self.assertIn('N/A',u.quote_note(item))
        d['quotes']['MSFT']['price_date']='2026-11-16'
        d['quotes']['MSFT']['currency']='HKD'
        self.assertIn('N/A',u.quote_note(item))

    def test_tool_quote_keeps_after_hours_timestamp_without_fake_url(self):
        quote=dict(source='web.run finance',price_date='2026-11-16',
                   price_basis='latest_trade',price_timestamp_utc='2026-11-17T00:58:31Z')
        note=u.quote_citation(quote,'ALAB -10.0%')
        self.assertNotIn('](web.run',note)
        self.assertIn('web.run finance',note)
        self.assertIn('纽约 2026-11-16',note)
        self.assertIn('UTC 2026-11-17T00:58:31Z',note)
        self.assertIn('盘后最新成交',note)
        self.assertNotIn('收盘',note)


if __name__=='__main__':
    unittest.main()
