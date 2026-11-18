"""Fourth batch: source exceptions, instrument boundaries and complete coverage."""
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import generate_13f_trends as g
import build_13f_snapshot as b
import update_13f_institutions as u
import propagate_13f_batch as p


class BatchFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault = Path(os.environ.get('INVESTORS_VAULT', g.DEFAULT_VAULT))
        cls.directory = cls.vault/'raw/data/13f-20261117-batch4'
        cls.data = {k:json.loads((cls.directory/f'{k}.json').read_text()) for k in g.BATCH4_MANAGERS}
        cls.periods = {k:g.resolve_filings(d) for k,d in cls.data.items()}

    def test_totals_coverage_and_immutable_provenance(self):
        expected = {'third-point':(4589115363,39),'kensico':(4965214586,23),
                    'maverick':(12820348682,502),'baupost':(5045853000,21),
                    'baillie':(105895756538,278),'greenlight':(3553265746,45),
                    'lone-pine':(15329467248,31),'tudor':(76623373608,3508)}
        for k, pair in expected.items():
            qs = self.periods[k]
            self.assertEqual(len(qs),16)
            self.assertEqual((qs[0]['date'],qs[-1]['date']),('2022-12-31','2026-09-30'))
            self.assertEqual((qs[-1]['total'],len(qs[-1]['rows'])),pair)
            self.assertTrue(set(qs[-1]['rows']) <= g.selected_keys(self.data[k],qs))
        for filename,digest in json.loads((self.directory/'sha256.json').read_text()).items():
            self.assertEqual(hashlib.sha256((self.directory/filename).read_bytes()).hexdigest(),digest,filename)

    def test_baupost_units_and_zero_value_peers(self):
        f=self.periods['baupost'][-1]['filings'][-1]
        self.assertEqual((f['reported_total_raw'],f['unit_multiplier']),(5045853,1000))
        self.assertEqual({x['multiplier'] for x in f['unit_evidence']},{1000})
        self.assertIsNone(b.compare_unit(100,0))
        self.assertIsNone(b.compare_unit(0,100))

    def test_tudor_count_exceptions_are_exact_file_exceptions(self):
        data=self.data['tudor']
        for acc, counts in [('0000950123-23-002502',(2299,2300)),('0000950123-23-005121',(2335,2336))]:
            f=next(f for f in data['filings'] if f['accessionNumber']==acc)
            content=(self.directory/f['local_source']).read_bytes()
            parsed=g.parse_filing(content,f)
            self.assertEqual((parsed['reported_count'],len(parsed['rows'])),counts)
            self.assertEqual(parsed['cover_difference_raw'],0)
            with self.assertRaises(ValueError):g.parse_filing(content+b'\n',f)

    def test_tudor_restatement_then_supplement_keeps_full_portfolio(self):
        q=next(q for q in self.periods['tudor'] if q['date']=='2025-09-30')
        self.assertEqual([f.get('amendment_type') for f in q['filings']][-2:],['RESTATEMENT','NEW HOLDINGS'])
        self.assertGreater(len(q['rows']),3000)
        for f in q['filings'][-2:]:
            self.assertTrue(set(g.aggregate(f['rows'])) <= q['rows'].keys())

    def test_greenlight_notices_and_scope_transition_are_not_sales(self):
        d=self.data['greenlight'];qs=self.periods['greenlight']
        self.assertTrue(any(f.get('notice') for f in d['filings']))
        before=next(q for q in qs if q['date']=='2023-12-31');after=next(q for q in qs if q['date']=='2024-03-31')
        result=g.attribution_breakdown(d,before,after)
        self.assertEqual((result['active'],result['price']),(0,0))
        self.assertAlmostEqual(result['unattributed'],after['total']-before['total'],delta=.01)
        self.assertIn('主体切换',g.format_change(d,before,after,next(iter(after['rows']))))

    def test_teva_one_for_one_conversion_is_a_continuing_position(self):
        d=self.data['greenlight'];a,z=self.periods['greenlight'][-2:]
        key=next(k for k,r in z['rows'].items() if g.security(d,r).get('ticker')=='TEVA' and not k[2])
        self.assertEqual(a['rows'][key]['cusip'],'881624209')
        self.assertEqual(z['rows'][key]['cusip'],'M8769Q102')
        self.assertEqual((a['rows'][key]['shares'],z['rows'][key]['shares']),(2886059,1817146))
        self.assertAlmostEqual(g.change(d,a,z,key)[1],1817146/2886059-1)

    def test_instruments_do_not_enter_common_stock_ranking(self):
        row=dict(issuer='Schwab U.S. Fund',security_class='EXCHANGE-TRADED FUND',put_call='',share_type='SH',cusip='fixture')
        self.assertEqual(u.category(row,'ETF'),'ETF')
        preferred=dict(row,issuer='Alphabet',security_class='CONVERTIBLE PREFERRED EQUITY')
        self.assertFalse(g.comparable({'securities':{}},preferred))
        d=self.data['tudor'];a,z=self.periods['tudor'][-2:]
        self.assertEqual(sum(bool(k[2]) for k in z['rows']),1760)
        self.assertNotIn('SPY',p.selected_companies(d,a,z))
        self.assertNotIn('XLU',p.selected_companies(d,a,z))

    def test_ambiguous_class_migration_is_not_a_sale_and_purchase(self):
        cusip='097023105'
        ordinary=(cusip,'EQUITY',''); preferred=(cusip,'CONVERTIBLE PREFERRED EQUITY','')
        row={'cusip':cusip,'shares':100,'value':1000,'put_call':''}
        before={'date':'2026-06-30','rows':{ordinary:row},'filings':[{'url':'https://www.sec.gov/example'}]}
        after={'date':'2026-09-30','rows':{preferred:dict(row,value=1200)},'filings':before['filings']}
        data={'class_identity_issues':[{'cusip':cusip,'put_call':''}]}
        parts=g.attribution_breakdown(data,before,after)
        self.assertEqual((parts['active'],parts['price'],parts['unattributed']),(0,0,200))
        self.assertIn('证券类别变化',g.format_change(data,before,after,preferred))

    def test_distributions_are_not_stock_splits_or_cash_purchases(self):
        d=self.data['tudor']
        for ticker,date in [('J','2024-09-30'),('J','2025-05-16'),('WDC','2025-02-24'),('CTVA','2026-10-01')]:
            self.assertFalse(any(s['ticker']==ticker and s['date']==date for s in d['splits']))
        ryanair=next(s for s in d['splits'] if s['ticker']=='RYAAY' and s['date']=='2024-09-30')
        self.assertEqual(ryanair['ratio'],2.5)
        d=self.data['greenlight'];a,z=self.periods['greenlight'][-2:]
        key=next(k for k,r in z['rows'].items() if r['cusip']=='001026103')
        self.assertEqual(g.change(d,a,z,key)[0],0)
        with mock.patch.object(u,'CROSS_KEYS',('greenlight',)),mock.patch.object(u,'read',return_value=(d,self.periods['greenlight'])):
            rows,_=u.cross_data()
        adig=next(r for r in rows if r['ticker']=='ADIG')
        self.assertEqual((adig['buy'],adig['sell'],adig['active']),(0,0,0))

    def test_share_and_weight_directions_and_all_quarter_reconciliation(self):
        for manager,ticker in [('baillie','MRNA'),('greenlight','DHT')]:
            d=self.data[manager];a,z=self.periods[manager][-2:]
            key=next(k for k,r in z['rows'].items() if g.security(d,r).get('ticker')==ticker and not k[2])
            self.assertLess(g.change(d,a,z,key)[0],0)
            self.assertGreater(g.weight(z,key)-g.weight(a,key),0)
            self.assertIn(key,set(g.top(z))-set(g.top(a)))
        for key,qs in self.periods.items():
            for a,z in zip(qs,qs[1:]):
                parts=[g.attribution_breakdown(self.data[key],a,z,option) for option in (False,True)]
                self.assertAlmostEqual(sum(x['total_change'] for x in parts),z['total']-a['total'],delta=.01)

    def test_quotes_use_requested_day_or_explicit_gap(self):
        for key,d in self.data.items():
            for ticker in d['editorial']['candidates']:
                quote=d.get('quotes',{}).get(ticker,{})
                self.assertTrue(quote, (key,ticker))
                if quote.get('price'):
                    self.assertEqual(quote['price_date'],'2026-11-16')
                else:self.assertTrue(quote.get('error'),(key,ticker))


if __name__=='__main__':unittest.main()
