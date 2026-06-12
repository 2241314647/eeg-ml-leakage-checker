from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from eeg_leakage_checker.checker import analyze_csv, generate_demo_csv


class LeakageCheckerSmokeTest(unittest.TestCase):
    def test_demo_flags_high_risk_leakage(self) -> None:
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "demo.csv"
            generate_demo_csv(csv_path)
            report = analyze_csv(csv_path)
        self.assertEqual(report.risk_level, "high")
        self.assertTrue(any("multiple splits" in finding.title for finding in report.findings))


if __name__ == "__main__":
    unittest.main()
