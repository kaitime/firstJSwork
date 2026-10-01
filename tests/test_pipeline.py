import json, pathlib, subprocess, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from commerce_agent.schema import Evidence
from commerce_agent import economics

class T(unittest.TestCase):
    def test_fact_requires_source(self):
        with self.assertRaises(ValueError):
            Evidence("x", "price", "FACT", "c", "", "").validate()
    def test_econ(self):
        fees = json.loads(pathlib.Path("config.json").read_text())["fees"]
        net, _ = economics.net_per_sale(10, 0, "gumroad", fees)
        self.assertEqual(net, 9.0)
        self.assertIsNone(economics.table(0.1, 5, "gumroad", fees, [100])["rows"][0]["sales_needed"])
    def test_end_to_end_degrades(self):
        r = subprocess.run([sys.executable, "run.py"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(pathlib.Path("output/opportunities.json").read_text())
        self.assertTrue(any("INSUFFICIENT" in o["status"] for o in d))

if __name__ == "__main__":
    unittest.main()
