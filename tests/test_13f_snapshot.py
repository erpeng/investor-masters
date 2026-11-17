"""Regression checks for evidence-sensitive snapshot normalization."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_13f_snapshot import apply_charts, compare_unit, filing_unit, legacy_page, nominal_price


class SnapshotEvidenceTests(unittest.TestCase):
    def test_each_filing_unit_is_inferred_and_conflict_rejected(self):
        charts = {
            'AAPL': {'daily_closes': {'2026-09-30': 200}, 'source': 'AAPL quote'},
            'MSFT': {'daily_closes': {'2026-09-30': 500}, 'source': 'MSFT quote'},
        }
        filing = {'accessionNumber': 'one', 'reportDate': '2026-09-30', 'rows': [
            {'cusip': '037833100', 'shares': 100, 'value_raw': 20, 'share_type': 'SH', 'put_call': ''},
        ]}
        self.assertEqual(filing_unit(filing, charts, {})[0], 1000)
        filing['rows'][0]['value_raw'] = 20000
        self.assertEqual(filing_unit(filing, charts, {})[0], 1)
        filing['rows'].append({'cusip': '594918104', 'shares': 100, 'value_raw': 50,
                              'share_type': 'SH', 'put_call': ''})
        with self.assertRaisesRegex(ValueError, 'Conflicting unit evidence'):
            filing_unit(filing, charts, {})
        self.assertIsNone(compare_unit(100, 500))

    def test_historical_anchor_reverses_subsequent_split_adjustment(self):
        chart = {'daily_closes': {'2024-03-28': 90},
                 'splits': [{'date': '2024-06-10', 'ratio': 10}]}
        self.assertEqual(nominal_price(chart, '2024-03-31'), (900, '2024-03-28'))
        self.assertIsNone(nominal_price(chart, '2024-04-10'))

    def test_option_unit_anchor_is_underlying_not_premium(self):
        filing = {'accessionNumber': 'put-report', 'reportDate': '2026-09-30', 'rows': [
            {'cusip': '037833100', 'shares': 100, 'value_raw': 20000, 'share_type': 'SH', 'put_call': 'PUT'}]}
        charts = {'AAPL': {'daily_closes': {'2026-09-30': 200}, 'source': 'quote'}}
        unit, evidence = filing_unit(filing, charts, {})
        self.assertEqual(unit, 1)
        self.assertIn('not option premium', evidence[0]['price_basis'])

    def test_stale_quote_is_not_presented_as_current(self):
        data = {'securities': {'A': {'ticker': 'OLD'}}, 'editorial': {}}
        apply_charts(data, {'OLD': {'price': 10, 'price_date': '2025-01-01',
                                  'requested_end': '2026-11-16', 'source': 'quote',
                                  'fetched_at': 'now', 'splits': []}})
        self.assertIsNone(data['quotes']['OLD']['price'])
        self.assertTrue(data['quotes']['OLD']['stale'])
        self.assertEqual(data['quotes']['OLD']['last_available_price'], 10)

    def test_spinoff_price_adjustments_do_not_change_parent_share_count(self):
        data = {'securities': {'A': {'ticker': 'GE'}, 'B': {'ticker': 'NVDA'}}, 'editorial': {}}
        common = {'price': 100, 'price_date': '2026-11-16', 'requested_end': '2026-11-16',
                  'source': 'quote', 'fetched_at': 'now'}
        apply_charts(data, {'GE': dict(common, splits=[{'date': '2024-04-02', 'ratio': 1.253}]),
                            'NVDA': dict(common, splits=[{'date': '2024-06-10', 'ratio': 10}])})
        self.assertEqual([(s['ticker'], s['ratio']) for s in data['splits']], [('NVDA', 10)])
        self.assertEqual(data['audit']['excluded_price_adjustments'][0]['ticker'], 'GE')

    def test_legacy_archive_preserves_method_and_old_watch_basket(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'vault/wiki/institutions/13F趋势-HH.md'
            source.parent.mkdir(parents=True)
            source.write_text('## 轨迹\n|BRK.B（伯克希尔）|1|\n|NVDA（英伟达） CALL|2|\n'
                              '## 三、用段永平的方法重新读\n长期方法。\n## 来源\n旧来源。')
            data = {'institution': 'hh', 'title': 'HH', 'editorial': {}}
            archived = legacy_page(data, root / 'vault', root / 'stage')
            self.assertEqual(data['editorial']['watch'], ['BRK-B', 'NVDA'])
            self.assertEqual(data['editorial']['legacy_method'], '长期方法。')
            source.write_text('new page')
            legacy_page(data, root / 'vault', root / 'stage')
            self.assertIn('旧来源。', archived.read_text())


if __name__ == '__main__':
    unittest.main()
