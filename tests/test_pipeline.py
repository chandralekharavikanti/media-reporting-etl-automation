import tempfile, unittest
from pathlib import Path
from src.generate_sample_data import out
from src.pipeline import run, validate

class PipelineTests(unittest.TestCase):
    def test_negative_metric(self):
        self.assertEqual(validate("traffic",{"date":"2025-01-01","publication":"A","sessions":"-1","pageviews":"10"}),"negative sessions")
    def test_missing_field(self):
        self.assertEqual(validate("payments",{"campaign_id":"C1"}),"missing paid_revenue")
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(out,Path(d)),0)
            self.assertTrue((Path(d)/"monthly_summary.csv").exists())

if __name__=="__main__":
    unittest.main()
