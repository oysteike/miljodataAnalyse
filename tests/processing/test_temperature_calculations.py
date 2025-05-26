import unittest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from processing import temperature_calculations as tc

class TestTemperatureCalculations(unittest.TestCase):
    def setUp(self):
        # Eksempeldata for januar, februar, mars 2022 og 2023
        self.df = pd.DataFrame({
            'referenceTimestamp': pd.to_datetime([
                '2022-01-15', '2022-02-15', '2022-03-15',
                '2023-01-15', '2023-02-15', '2023-03-15'
            ]),
            'value': [-2.0, -3.0, 1.0, 0.0, -2.0, 2.0]
        })

    def test_calculate_monthly_anomalies(self):
        anomalies = tc.calculate_monthly_anomalies(self.df.copy())
        self.assertIn('anomaly', anomalies.columns)
        # Sjekk at anomali = value - normal
        jan_normal = -4.3
        self.assertAlmostEqual(anomalies.iloc[0]['anomaly'], -2.0 - jan_normal, places=2)

    def test_assess_annual_progress(self):
        anomalies = tc.calculate_monthly_anomalies(self.df.copy())
        annual_anomaly, progress = tc.assess_annual_progress(anomalies)
        self.assertIn('latest_year', progress)
        self.assertIn('on_track', progress)
        self.assertEqual(annual_anomaly.shape[1], 2)  # year, anomaly

    def test_required_reduction(self):
        anomalies = tc.calculate_monthly_anomalies(self.df.copy())
        annual_anomaly, _ = tc.assess_annual_progress(anomalies)
        reduction = tc.required_reduction(annual_anomaly, target=1.5)
        self.assertIsInstance(reduction, float)

    def test_load_all_temperature_data_invalid(self):
        # Skal returnere tom DataFrame hvis katalog ikke finnes
        df = tc.load_all_temperature_data("not_a_real_dir")
        self.assertTrue(df.empty)

    def test_analyze_temperature_progress_invalid(self):
        # Skal returnere (None, None, None) hvis kolonner mangler
        result = tc.analyze_temperature_progress("not_a_real_dir")
        self.assertEqual(result, (None, None, None))

if __name__ == '__main__':
    unittest.main()