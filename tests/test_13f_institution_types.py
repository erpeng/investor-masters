"""Regression cases for issuer names and 13F security classes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from update_13f_institutions import category, instrument_type


class InstrumentTypesTest(unittest.TestCase):
    def row(self, issuer, security_class, put_call=""):
        return {"issuer": issuer, "security_class": security_class,
                "put_call": put_call, "cusip": "fixture"}

    def test_netflix_is_equity_not_etf_substring(self):
        row = self.row("NETFLIX INC", "COM")
        self.assertEqual(instrument_type(row), "普通股")
        self.assertEqual(category(row, "NFLX"), "普通股票")

    def test_brazil_fund_and_its_call_stay_separate(self):
        stock = self.row("ISHARES INC", "MSCI BRAZIL ETF")
        option = dict(stock, put_call="CALL")
        self.assertEqual(category(stock, "EWZ"), "ETF")
        self.assertEqual(category(option, "EWZ"), "期权")

    def test_ads_is_retained_as_equity_with_instrument_tag(self):
        row = self.row("PDD HOLDINGS INC", "SPON ADS")
        self.assertEqual(instrument_type(row), "ADR/ADS")
        self.assertEqual(category(row, "PDD"), "普通股票")

    def test_asml_registry_share_is_not_an_adr(self):
        row = self.row("ASML HOLDING N V", "N Y REGISTRY SHS")
        self.assertEqual(instrument_type(row), "纽约登记股")
        self.assertEqual(category(row, "ASML"), "普通股票")


if __name__ == "__main__":
    unittest.main()
