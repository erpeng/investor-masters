"""Regression checks against independently reviewed SEC Q2/Q3 observations."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('trends', ROOT / 'scripts/generate_13f_trends.py')
trends = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trends)


class FiveInstitutionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        vault = Path(os.environ.get('INVESTORS_VAULT', trends.DEFAULT_VAULT))
        cls.directory = vault / 'raw/data/13f-20261117'
        cls.data = {k: json.loads((cls.directory / f'{k}.json').read_text()) for k in trends.MANAGERS}
        cls.periods = {k: trends.resolve_filings(v) for k,v in cls.data.items()}

    def test_complete_history_and_latest_totals(self):
        expected = {'berkshire': (304196581325, 30), 'himalaya': (3781431260, 8),
                    'hh': (17190742843, 16), 'duquesne': (4470867000, 65),
                    'appaloosa': (7559628593, 24)}
        for key, (total, count) in expected.items():
            with self.subTest(institution=key):
                qs = self.periods[key]
                self.assertEqual(len(qs), 16)
                self.assertEqual((qs[0]['date'], qs[-1]['date']), ('2022-12-31', '2026-09-30'))
                self.assertEqual(qs[-1]['total'], total)
                self.assertEqual(len(qs[-1]['rows']), count)

    def row(self, manager, cusip, offset=-1, option=''):
        q = self.periods[manager][offset]
        keys = [k for k in q['rows'] if k[0] == cusip and k[2] == option]
        self.assertEqual(len(keys), 1)
        return keys[0], q['rows'][keys[0]]

    def test_known_share_changes_and_price_only_weight_rises(self):
        checks = [('himalaya','722304102',1000000), ('himalaya','88034P109',8233628),
                  ('hh','67066G104',-3961200), ('duquesne','874039100',-556980),
                  ('duquesne','632307104',-25640), ('appaloosa','595112103',275000),
                  ('appaloosa','67066G104',475000), ('berkshire','037833100',0)]
        for manager, cusip, diff in checks:
            key, _ = self.row(manager,cusip)
            prev, curr = self.periods[manager][-2:]
            self.assertEqual(trends.change(self.data[manager],prev,curr,key)[0], diff)
        for manager,cusip in [('berkshire','037833100'), ('duquesne','632307104')]:
            key,_ = self.row(manager,cusip)
            prev,curr = self.periods[manager][-2:]
            self.assertGreater(trends.weight(curr,key), trends.weight(prev,key))

    def test_units_and_rounding_retain_original_evidence(self):
        f = next(f for f in self.data['duquesne']['filings'] if f['reportDate']=='2026-09-30')
        self.assertEqual(f['reported_total_raw'],4470866)
        self.assertEqual(f['cover_difference_raw'],1)
        self.assertEqual(f['unit_multiplier'],1000)
        self.assertTrue(f.get('unit_evidence'))
        for d in self.data.values():
            for f in d['filings']:
                if f.get('notice'):
                    continue
                self.assertEqual(len(f['rows']),f['reported_count'])
                self.assertEqual(sum(r['value_raw'] for r in f['rows'])-f['reported_total_raw'],f['cover_difference_raw'])
                for row in f['rows']:
                    self.assertEqual(row['value'],row['value_raw']*f['unit_multiplier'])

    def test_company_actions_and_class_spelling_are_not_trades(self):
        key,_ = self.row('duquesne','94352A104')
        prev,curr = self.periods['duquesne'][-2:]
        self.assertEqual(trends.change(self.data['duquesne'],prev,curr,key)[0],0)
        for manager,cusip in [('himalaya','722304102'),('duquesne','23306J309')]:
            self.assertEqual(len({k for q in self.periods[manager] for k in q['rows'] if k[0]==cusip}),1)
        d = {'splits':[{'ticker':'TEST','date':'2026-08-01','ratio':5}],
             'securities':{'000000001':{'ticker':'TEST','name':'Test'}}}
        old = dict(issuer='Test',cusip='000000001',security_class='COM',put_call='',share_type='SH',shares=100,value=5000)
        new = dict(old,shares=500)
        k = trends.identity(old)
        p = dict(date='2026-06-30',rows={k:old});q=dict(date='2026-09-30',rows={k:new})
        self.assertEqual(trends.change(d,p,q,k),(0,0))
        self.assertEqual(trends.attribution(d,p,q),(0,0))
        app=self.periods['appaloosa']
        p=next(q for q in app if q['date']=='2024-09-30')
        q=next(q for q in app if q['date']=='2024-12-31')
        k=next(k for k in q['rows'] if k[0]=='512807306' and not k[2])
        self.assertIn(k,p['rows'])
        self.assertEqual(trends.change(self.data['appaloosa'],p,q,k),(250000, .25))
        self.assertFalse(any(s['ticker']=='GE' and s['date'] in ('2023-01-04','2024-04-02')
                             for s in self.data['duquesne']['splits']))

    def test_options_are_separate_and_not_shares_sold(self):
        q2,q3 = self.periods['appaloosa'][-2:]
        self.assertIn(('037833100','COM','PUT'),q2['rows'])
        self.assertFalse(any(k[2] for k in q3['rows']))
        q = self.periods['duquesne'][-1]
        self.assertEqual(len([k for k in q['rows'] if k[0]=='023135106']),2)
        self.assertEqual(len([k for k in q['rows'] if k[2]=='CALL']),5)

    def test_reviewed_supplement_and_unreviewed_conflict(self):
        q = next(q for q in self.periods['berkshire'] if q['date']=='2025-03-31')
        key = next(k for k in q['rows'] if k[0]=='526057302')
        self.assertEqual(q['rows'][key]['shares'],152774)
        data = copy.deepcopy(self.data['berkshire'])
        f = next(f for f in data['filings'] if f['accessionNumber']=='0000950123-25-008361')
        f['additive_overlap_cusips']=[]
        with self.assertRaisesRegex(ValueError,'Conflicting amendment'):
            trends.resolve_filings(data)
        row=dict(cusip='000000001',security_class='COM',put_call='',share_type='SH',shares=100,value=1000)
        original=dict(reportDate='2026-03-31',filingDate='2026-05-01',accessionNumber='a',form='13F-HR',rows=[row])
        addition=dict(original,filingDate='2026-05-02',accessionNumber='b',form='13F-HR/A',amendment_type='NEW HOLDINGS',additive_overlap_cusips=['000000001'])
        result=trends.resolve_filings({'filings':[original,addition]})
        self.assertEqual(next(iter(result[0]['rows'].values()))['shares'],200)

    def test_attribution_reconciles_all_quarters(self):
        for manager,qs in self.periods.items():
            for prev,curr in zip(qs,qs[1:]):
                with self.subTest(manager=manager,date=curr['date']):
                    terms=trends.attribution(self.data[manager],prev,curr)+trends.attribution(self.data[manager],prev,curr,True)
                    self.assertAlmostEqual(sum(terms),curr['total']-prev['total'],delta=.01)

    def test_sirius_exchange_uses_three_predecessors(self):
        qs=self.periods['berkshire'];d=self.data['berkshire']
        p=next(q for q in qs if q['date']=='2024-06-30')
        q=next(q for q in qs if q['date']=='2024-09-30')
        exchange=trends.conversion(d,p,q)
        self.assertAlmostEqual(exchange['shares'],101380355.95,places=2)
        self.assertEqual(q['rows'][exchange['target']]['shares'],105155029)
        self.assertAlmostEqual(trends.change(d,p,q,exchange['target'])[1],.0372327851,places=7)
        self.assertIn('换股后',trends.format_change(d,p,q,exchange['target']))

    def test_latest_all_securities_and_historical_top_ten_render(self):
        for manager,data in self.data.items():
            qs=self.periods[manager]
            result=trends.render(data,qs)
            self.assertEqual(result,trends.render(copy.deepcopy(data),trends.resolve_filings(copy.deepcopy(data))))
            trajectory=result.split('## 重点标的季度轨迹')[1].split('## 逐季度行为解读')[0]
            for key in trends.selected_keys(data,qs):
                row=next(q['rows'][key] for q in reversed(qs) if key in q['rows'])
                self.assertIn(trends.label(data,row),trajectory)
            self.assertIn('2026Q3',trajectory)
            self.assertIn('2023Q1',trajectory)
            self.assertIn('### 反向复盘',result)

    def test_quote_missing_never_becomes_zero_or_recommendation(self):
        data=copy.deepcopy(self.data['himalaya'])
        data['quotes']={}
        _,row=self.row('himalaya','722304102')
        cells=trends.price_cells(data,row,'2026-09-30')
        self.assertEqual(cells[1:3],('N/A','N/A'))
        self.assertIn('行情缺失',cells[-1])
        data['quotes']={'PDD':{'price':100,'currency':'USD','price_date':'2024-09-30'}}
        cells=trends.price_cells(data,row,'2026-09-30')
        self.assertEqual(cells[1:3],('N/A','N/A'))
        self.assertIn('过期',cells[-1])
        for d in self.data.values():
            for quote in d.get('quotes',{}).values():
                if quote.get('price'):
                    self.assertLessEqual(quote['price_date'],d['as_of'])
                    self.assertTrue(quote.get('source'))

    def test_source_files_match_frozen_checksums(self):
        for d in self.data.values():
            for f in d['filings']:
                if f.get('notice'):
                    continue
                raw=self.directory/'sec'/f'{f["accessionNumber"]}.txt'
                self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),f['sha256'])


if __name__ == '__main__':
    unittest.main()
