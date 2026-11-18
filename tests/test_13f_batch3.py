"""Reviewed third-batch amounts, amendments, identities and corporate actions."""
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import generate_13f_trends as g
import build_13f_snapshot as b
import update_13f_institutions as u


class BatchThreeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault=Path(os.environ.get('INVESTORS_VAULT',g.DEFAULT_VAULT))
        cls.directory=cls.vault/'raw/data/13f-20261117-batch3'
        cls.data={key:json.loads((cls.directory/f'{key}.json').read_text()) for key in g.BATCH3_MANAGERS}
        cls.periods={key:g.resolve_filings(d) for key,d in cls.data.items()}

    def test_coverage_totals_and_source_hashes(self):
        expected={'akre':(4424875808,21),'dorsey':(1712548933,13),'ako':(3154832000,18),
                  'giverny':(2917847112,51),'oakmark':(76774722322,176)}
        for key,(total,count) in expected.items():
            qs=self.periods[key]
            self.assertEqual(len(qs),16)
            self.assertEqual((qs[0]['date'],qs[-1]['date']),('2022-12-31','2026-09-30'))
            self.assertEqual((qs[-1]['total'],len(qs[-1]['rows'])),(total,count))
            self.assertTrue(all(g.security(self.data[key],r)['ticker'] for r in qs[-1]['rows'].values()))
        for filename,digest in json.loads((self.directory/'sha256.json').read_text()).items():
            self.assertEqual(hashlib.sha256((self.directory/filename).read_bytes()).hexdigest(),digest,filename)

    def test_ako_thousand_dollar_units_have_independent_evidence(self):
        latest=self.periods['ako'][-1]['filings'][-1]
        self.assertEqual(latest['reported_total_raw'],3154832)
        self.assertEqual(latest['unit_multiplier'],1000)
        self.assertGreater(len(latest['unit_evidence']),1)
        self.assertEqual({e['multiplier'] for e in latest['unit_evidence']},{1000})
        self.assertEqual(sum(r['value'] for r in latest['rows']),3154832000)

    def test_restatements_replace_and_new_holdings_deduplicate(self):
        q2=self.periods['giverny'][-2]
        self.assertEqual(q2['filings'][-1]['accessionNumber'],'0001641864-26-000010')
        self.assertEqual(q2['total'],2974321189)
        self.assertEqual(q2['filings'][0]['rows'],q2['filings'][1]['rows'])
        q3=next(q for q in self.periods['giverny'] if q['date']=='2025-09-30')
        self.assertEqual(q3['filings'][-1]['accessionNumber'],'0001641864-25-000012')
        self.assertEqual(q3['total'],2951143263)
        akre=next(q for q in self.periods['akre'] if q['date']=='2024-03-31')
        self.assertEqual(len(akre['rows']),21)
        self.assertEqual(akre['total'],12089164350)
        dorsey=next(q for q in self.periods['dorsey'] if q['date']=='2023-03-31')
        self.assertEqual(dorsey['filings'][-1]['accessionNumber'],'0001398344-23-013281')

    def test_same_cusip_class_spellings_remain_one_security(self):
        for cusip,a,z in [('02079K107','CAPSTKCLC','CAP STK CL C'),
                           ('57636Q104','COM','CL A'),('G54950103','SHS','COM'),
                           ('922908736','GROWTH ETF','MRNGSTR GRWT ETF')]:
            with self.subTest(cusip=cusip):
                row=dict(cusip=cusip,security_class=a,put_call='')
                self.assertEqual(g.identity(row),g.identity(dict(row,security_class=z)))
                self.assertNotEqual(g.identity(row),g.identity(dict(row,put_call='CALL')))
        # Alphabet A and C are still different share classes.
        self.assertNotEqual(g.identity(dict(cusip='02079K107',security_class='CAPSTKCLC',put_call='')),
                            g.identity(dict(cusip='02079K305',security_class='CAPSTKCLA',put_call='')))

    def test_distribution_is_not_a_parent_stock_split(self):
        data=self.data['oakmark']
        excluded={(e['ticker'],e['date']) for e in data['audit']['excluded_price_adjustments']}
        self.assertIn(('DHR','2023-10-02'),excluded)
        self.assertIn(('BDX','2026-02-10'),excluded)
        self.assertFalse(any(s['ticker']=='DHR' and s['date']=='2023-10-02' for s in data['splits']))
        splits={(s['ticker'],s['date']):s['ratio'] for s in data['splits']}
        self.assertEqual(splits['UL','2025-12-09'],8/9)
        self.assertEqual(splits['NFLX','2025-11-17'],10)
        self.assertTrue(any(s['ticker']=='ORLY' and s['ratio']==15 for s in self.data['akre']['splits']))

    def test_weights_and_shares_can_move_in_opposite_directions(self):
        for manager,ticker,direction in [('akre','MA',-1),('dorsey','APP',1)]:
            d=self.data[manager];p,q=self.periods[manager][-2:]
            key=next(k for k,r in q['rows'].items() if g.security(d,r)['ticker']==ticker and not k[2])
            self.assertGreater(g.change(d,p,q,key)[0]*direction,0)
            self.assertLess((g.weight(q,key)-g.weight(p,key))*direction,0)

    def test_all_quarters_reconcile_and_latest_securities_are_rendered(self):
        for manager,qs in self.periods.items():
            d=self.data[manager]
            for p,q in zip(qs,qs[1:]):
                parts=[g.attribution_breakdown(d,p,q,option) for option in (False,True)]
                self.assertAlmostEqual(sum(x['active']+x['price']+x['unattributed'] for x in parts),q['total']-p['total'],delta=.01)
            self.assertTrue(set(qs[-1]['rows'])<=g.selected_keys(d,qs))
            text=g.render(d,qs);trajectory=text.split('## 重点标的季度轨迹')[1].split('## 逐季度行为解读')[0]
            for row in qs[-1]['rows'].values():self.assertIn(g.label(d,row),trajectory)
            for line in trajectory.splitlines():
                if line.startswith('| '):self.assertEqual(len(line.split('|'))-2,16)
            self.assertIn('### 反向复盘',text)
            for ticker in d['editorial']['candidates']:
                quote=d['quotes'][ticker]
                self.assertEqual(quote['price_date'],'2026-11-16')
                self.assertGreater(quote['price'],0)

    def test_third_batch_scope_and_preserved_audit_route(self):
        paths,new,cross=u.configure_manifest(ROOT/'scripts/data/13f-2026q3-batches.json',self.vault)
        self.assertEqual(new,tuple(g.BATCH4_MANAGERS));self.assertEqual(len(cross),23)
        self.assertEqual(paths['berkshire'].parent.name,'13f-20261117')
        self.assertEqual(paths['fundsmith'].parent.name,'13f-20261117-batch2')
        self.assertEqual(g.audit_name(self.data['akre']),'Akre-13F-source-audit')
        text=(self.vault/'wiki/institutions/13F趋势-2026Q3.md').read_text()
        self.assertIn('23 家样本',text)
        self.assertNotIn('十家样本',text)
        self.assertIn('Harris Associates全部申报范围',text)


if __name__=='__main__':unittest.main()
