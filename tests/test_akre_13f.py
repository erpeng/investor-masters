"""Financial correctness checks for identities, amended filings and split attribution."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("akre", ROOT / "scripts/generate_akre_13f_trend.py")
akre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(akre)


class AkreEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        vault = Path(os.environ.get("INVESTORS_VAULT", "/Users/zhangshihua/Desktop/investors/investors"))
        cls.data = json.loads((vault / "raw/data/akre-13f-20261012.json").read_text())
        cls.quarters = akre.resolve_filings(cls.data)

    def test_new_holdings_amendment_does_not_double_count_original(self):
        q = next(q for q in self.quarters if q["date"] == "2024-03-31")
        self.assertEqual(len(q["rows"]), 21)
        self.assertEqual(q["total"], 12089164350)
        self.assertEqual(len(q["filings"]), 2)
        self.assertEqual(len(self.quarters), 15)

    def test_conflicting_supplement_requires_review(self):
        data = copy.deepcopy(self.data)
        amended = next(f for f in data["filings"] if f["form"] == "13F-HR/A")
        amended["rows"][0]["shares"] += 1
        with self.assertRaisesRegex(ValueError, "Ambiguous overlapping"):
            akre.resolve_filings(data)

    def test_security_identity_retains_class_and_option_side(self):
        rows = self.quarters[-1]["rows"]
        crm = [k for k in rows if k[0] == "79466L302"]
        self.assertEqual(len(crm), 2)
        self.assertEqual({k[2] for k in crm}, {"", "CALL"})
        sample = dict(cusip="48251w104", security_class=" com  units ", put_call=" ")
        self.assertEqual(akre.identity(sample), ("48251W104", "COM UNITS", ""))
        self.assertEqual(sum(r["value"] for r in rows.values()), 5122536308)

    def test_split_alone_is_not_buying_or_price_return(self):
        old = dict(cusip="67103H107", security_class="COM", put_call="", shares=100, value=150000)
        new = dict(old, shares=1500)
        k = akre.identity(old)
        p = dict(date="2025-03-31", rows={k: old})
        q = dict(date="2025-06-30", rows={k: new})
        self.assertEqual(akre.delta(self.data, p, q, k), (0, 0))
        self.assertEqual(akre.attribution(self.data, p, q), (0, 0))

    def test_attribution_reconciles_every_quarter_including_options(self):
        for p, q in zip(self.quarters, self.quarters[1:]):
            with self.subTest(date=q["date"]):
                terms = akre.attribution(self.data, p, q) + akre.attribution(self.data, p, q, options=True)
                self.assertAlmostEqual(sum(terms), q["total"] - p["total"], delta=.01)

    def test_latest_and_historical_top_ten_are_all_displayed(self):
        text = akre.render(self.data, self.quarters)
        trajectory = text.split("## 重点标的季度轨迹")[1].split("## 逐季度解读")[0]
        keys = set(self.quarters[-1]["rows"])
        for q in self.quarters[1:]:
            keys.update(akre.top(q))
        for k in keys:
            r = next(q["rows"][k] for q in reversed(self.quarters) if k in q["rows"])
            self.assertIn(akre.label(self.data, r), trajectory)
        self.assertIn("CRM（Salesforce） CALL", trajectory)
        self.assertIn("2023Q1", trajectory)


if __name__ == "__main__":
    unittest.main()
