"""Reviewed second-batch SEC observations and source-anomaly boundaries."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_13f_trends as g
from build_13f_snapshot import legacy_page


class BatchTwoEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(os.environ.get('BATCH2_SNAPSHOT_DIR') or
                             Path(os.environ.get('INVESTORS_VAULT', g.DEFAULT_VAULT)) / 'raw/data/13f-20261117-batch2')
        cls.data = {key: json.loads((cls.directory / f'{key}.json').read_text()) for key in g.BATCH2_MANAGERS}
        cls.periods = {key: g.resolve_filings(data) for key, data in cls.data.items()}

    def row(self, manager, cusip, offset=-1, option=''):
        q = self.periods[manager][offset]
        matches = [(key, row) for key, row in q['rows'].items() if key[0] == cusip and key[2] == option]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_first_batch_default_is_unchanged(self):
        self.assertEqual(list(g.MANAGERS), ['berkshire', 'himalaya', 'hh', 'duquesne', 'appaloosa'])
        self.assertTrue(set(g.MANAGERS) | set(g.BATCH2_MANAGERS) <= set(g.ALL_MANAGERS))

    def test_complete_coverage_and_latest_totals(self):
        expected = {'atreides': (17994718085, 46), 'coatue': (54495247703, 73),
                    'altimeter': (10308735663, 17), 'fundsmith': (12922460889, 42),
                    'pershing': (30796550126, 16)}
        for key, (total, count) in expected.items():
            qs = self.periods[key]
            with self.subTest(manager=key):
                self.assertEqual(len(qs), 16)
                self.assertEqual((qs[0]['date'], qs[-1]['date']), ('2022-12-31', '2026-09-30'))
                self.assertEqual(qs[-1]['total'], total)
                self.assertEqual(len(qs[-1]['rows']), count)

    def test_pershing_lineage_notice_and_supplement(self):
        data = self.data['pershing']
        self.assertEqual([x['cik'] for x in data['cik_lineage']], [1336528, 2026053])
        notices = [f for f in data['filings'] if f.get('notice')]
        self.assertTrue(any(f['reportDate'] == '2026-09-30' for f in notices))
        q2 = self.periods['pershing'][-2]
        self.assertEqual(q2['total'], 25521452281)
        key, old = self.row('pershing', '71531U102', -2)
        _, new = self.row('pershing', '71531U102')
        self.assertEqual((old['shares'], new['shares']), (184289699, 184289699))
        self.assertEqual(g.change(data, q2, self.periods['pershing'][-1], key), (0, 0))
        self.assertFalse(g.comparable(data, new))
        self.assertTrue(any(f.get('amendment_type') == 'NEW HOLDINGS' for f in q2['filings']))
        self.assertTrue(any(f['reportDate'] == '2026-03-31' for f in data['excluded_lineage_filings']))
        self.assertEqual(old['other_managers'], ['3', '4'])
        self.assertIn('3, 4', old['other_managers_raw'])

    def test_altimeter_cover_exception_is_exact_and_raw_retained(self):
        data = self.data['altimeter']
        filing = next(f for f in data['filings'] if f['reportDate'] == '2026-09-30')
        self.assertEqual(filing['cover_difference_raw'], -344388)
        self.assertEqual(filing['reported_total_raw'], 10309080051)
        raw = (self.directory / filing['local_source']).read_bytes()
        parsed = g.parse_filing(raw, filing)
        self.assertIsNotNone(parsed['cover_exception'])
        with self.assertRaisesRegex(ValueError, 'Cover mismatch'):
            g.parse_filing(raw, dict(filing, accessionNumber='unreviewed'))
        with self.assertRaisesRegex(ValueError, 'Cover mismatch'):
            g.parse_filing(raw.replace(b'<tableValueTotal>10309080051', b'<tableValueTotal>10309080052'), filing)
        _, grab = self.row('altimeter', 'G4124C117')
        self.assertEqual((grab['shares'], grab['value']), (3502000, 94554))
        self.assertEqual(grab['security_class'], 'W EXP 12/1/202')
        self.assertNotEqual(grab.get('value_reliable'), False)
        self.assertFalse(g.comparable(data, grab))
        self.assertEqual(g.price_cells(data, grab, '2026-09-30')[1:3], ('N/A', 'N/A'))

    def test_anomaly_is_unattributed_and_every_quarter_reconciles(self):
        for manager, qs in self.periods.items():
            for prev, curr in zip(qs, qs[1:]):
                parts = [g.attribution_breakdown(self.data[manager], prev, curr, option) for option in (False, True)]
                with self.subTest(manager=manager, period=curr['date']):
                    self.assertAlmostEqual(sum(p['total_change'] for p in parts), curr['total'] - prev['total'], delta=.01)
        # A future genuinely unreliable value must not be forced into price.
        p, q = copy.deepcopy(self.periods['altimeter'][-2:])
        key, old = self.row('altimeter', 'G4124C117', -2)
        q['rows'][key].update(value_reliable=False, value_issue='Synthetic unreliable value')
        result = g.attribution_breakdown(self.data['altimeter'], p, q)
        self.assertEqual(result['unattributed'], 94554 - old['value'])
        self.assertEqual(len(result['issues']), 1)
        self.assertEqual(g.attribution(self.data['altimeter'], p, q), (result['active'], result['price']))

    def test_same_security_class_and_cusip_case_do_not_create_trades(self):
        data = self.data['fundsmith']; p, q = self.periods['fundsmith'][-2:]
        key, row = self.row('fundsmith', '65290E101')
        self.assertIn(key, p['rows'])
        self.assertEqual(g.change(data, p, q, key)[0], 1333678)
        self.assertEqual((p['rows'][key]['security_class'], row['security_class']), ('CLASS A COM', 'COM'))
        p, q = self.periods['altimeter'][-2:]
        key, row = self.row('altimeter', '15675D103')
        self.assertEqual(g.change(self.data['altimeter'], p, q, key)[0], -1271533)
        self.assertFalse(g.comparable(self.data['altimeter'], row))
        alphabet = [k for k in self.periods['coatue'][-1]['rows'] if k[0] in ('02079K305', '02079K107')]
        self.assertEqual(len(alphabet), 2)
        for cusip in ('13646K108', '44267T102'):
            self.assertEqual(len({key for q in self.periods['pershing'] for key in q['rows'] if key[0] == cusip}), 1)
        self.assertFalse(any(s['ticker'] == 'HHH' and s['date'] == '2024-08-01'
                             for s in self.data['pershing']['splits']))

    def test_coatue_other_managers_survive_aggregation(self):
        data = self.data['coatue']
        filing = next(f for f in data['filings'] if f['reportDate'] == '2026-09-30')
        self.assertEqual(len(filing['rows']), 263)
        self.assertEqual(len(filing['other_manager_definitions']), 27)
        self.assertTrue(any(len(row.get('other_managers', [])) > 1 for row in self.periods['coatue'][-1]['rows'].values()))

    def test_reviewed_historical_continuity_and_complex_action_boundary(self):
        for manager, cusip in [('atreides', '833445109'), ('coatue', '82509L107'),
                               ('altimeter', '770700102'), ('altimeter', 'G4124C117')]:
            keys = {key for q in self.periods[manager] for key in q['rows'] if key[0] == cusip}
            self.assertEqual(len(keys), 1, (manager, cusip))
        d = self.data['coatue']; qs = self.periods['coatue']
        p = next(q for q in qs if q['date'] == '2025-06-30')
        q = next(q for q in qs if q['date'] == '2025-09-30')
        key = next(k for k in q['rows'] if k[0] == '549498202')
        self.assertIn(key, p['rows'])
        self.assertAlmostEqual(g.change(d, p, q, key)[0], -.1, places=4)
        p = next(q for q in qs if q['date'] == '2023-06-30')
        q = next(q for q in qs if q['date'] == '2023-09-30')
        key = next(k for k in q['rows'] if k[0] == '00165C302')
        self.assertIn(key, p['rows'])
        self.assertEqual(g.change(d, p, q, key), (0, None))
        self.assertIn('公司行动待核', g.format_change(d, p, q, key))
        self.assertEqual(g.attribution_breakdown(d, p, q)['unattributed'], 1822807 - 14510126)

    def test_quote_basis_and_special_adr_are_visible(self):
        d = self.data['coatue']
        _, row = self.row('coatue', '78392B206')
        self.assertIn('[ADR/ADS]', g.label(d, row))
        self.assertFalse(g.comparable(d, row))
        _, crm = self.row('coatue', '79466L302')
        cells = g.price_cells(d, crm, '2026-09-30')
        self.assertIn('盘后', cells[1])
        self.assertIn('Z', cells[1])
        text = g.render(d, self.periods['coatue'])
        self.assertNotIn('](web.run finance)', text)
        self.assertEqual(d['quotes']['CRM']['source'], 'web.run finance')

    def test_atreides_ordinary_and_options_remain_separate(self):
        q = self.periods['atreides'][-1]
        ordinary = g.ordinary_slice(q)
        self.assertEqual(len(ordinary['rows']), 41)
        self.assertEqual(ordinary['total'], 10741425085)
        self.assertEqual(q['total'] - ordinary['total'], 7253293000)
        self.assertEqual(len([key for key in q['rows'] if key[2]]), 5)
        text = g.render(self.data['atreides'], self.periods['atreides'])
        self.assertIn('非期权证券集中度', text)

    def test_frozen_evidence_and_deterministic_render(self):
        manifest = json.loads((self.directory / 'sha256.json').read_text())
        for path, expected in manifest.items():
            self.assertEqual(hashlib.sha256((self.directory / path).read_bytes()).hexdigest(), expected, path)
        for manager, data in self.data.items():
            rendered = g.render(data, self.periods[manager])
            self.assertEqual(rendered, g.render(copy.deepcopy(data), g.resolve_filings(copy.deepcopy(data))))
            trajectory = rendered.split('## 重点标的季度轨迹')[1].split('## 逐季度行为解读')[0]
            for key in g.selected_keys(data, self.periods[manager]):
                row = next(q['rows'][key] for q in reversed(self.periods[manager]) if key in q['rows'])
                self.assertIn(g.label(data, row), trajectory)


class LegacyMethodExtractionTests(unittest.TestCase):
    def test_unnumbered_institution_method_is_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'vault/wiki/institutions/13F趋势-Atreides.md'
            source.parent.mkdir(parents=True)
            source.write_text('## 用 Atreides 的方法重新读\n研究公开与私募交界。\n## 来源\nsource')
            data = {'institution': 'atreides', 'title': 'Atreides', 'editorial': {}}
            legacy_page(data, root / 'vault', root / 'stage')
            self.assertEqual(data['editorial']['legacy_method'], '研究公开与私募交界。')


if __name__ == '__main__':
    unittest.main()
