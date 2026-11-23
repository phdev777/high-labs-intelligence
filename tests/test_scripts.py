"""Tests using only Python's standard library."""
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from budget_variance import analyze,parse_amount
from profile_tabular import csv_rows,profile

class AmountTests(unittest.TestCase):
    def test_br_and_us(self):
        self.assertEqual(parse_amount("R$ 1.234,56","br"),Decimal("1234.56"))
        self.assertEqual(parse_amount("$1,234.56","us"),Decimal("1234.56"))
        self.assertEqual(parse_amount("(1.234,56)","br"),Decimal("-1234.56"))
    def test_invalid(self):
        for raw in ("","N/A","5abc","NaN"):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                parse_amount(raw)
    def test_budget(self):
        obj,code=analyze(ROOT/"examples"/"custos-sinteticos.csv",["categoria","periodo"],"orcado","realizado","br")
        self.assertEqual(code,0)
        self.assertEqual(obj["status"],"ok")
        self.assertEqual(obj["total_orcado"],"6300")
        self.assertEqual(obj["total_realizado"],"6470")
        self.assertEqual(obj["total_variacao"],"170")
    def test_invalid_row_not_zero(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"x.csv"
            path.write_text("categoria;periodo;orcado;realizado\nTeste;2026-11;;4,00\n",encoding="utf-8")
            result,code=analyze(path,["categoria","periodo"],"orcado","realizado","br")
            self.assertEqual(code,2)
            self.assertEqual(result["invalid_rows"],1)

class ProfileTests(unittest.TestCase):
    def test_profile(self):
        gen=csv_rows(ROOT/"examples"/"producao-sintetica.csv",None)
        head,records,meta=next(gen)
        result=profile(head,records,"evento_id",0,100)
        self.assertEqual(result["rows_profiled"],3)
        self.assertEqual(result["duplicate_keys_in_observed_set"],0)
    def test_duplicate_key(self):
        result=profile(["id","valor"],iter([["x","1"],["x","2"],["y","3"]]),"id",0,1)
        self.assertEqual(result["duplicate_keys_in_observed_set"],1)
        self.assertTrue(result["key_uniqueness_check_limited"])
    def test_duplicate_headers_rejected(self):
        with self.assertRaises(ValueError):
            profile(["a","a"],iter([[1,2]]),None,0,100)

if __name__=="__main__":
    unittest.main()
