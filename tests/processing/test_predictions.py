import unittest
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.predictions import predict_from_csv

class TestPredictionPipeline(unittest.TestCase):
    
    def setUp(self):
        # Lag en midlertidig CSV med syntetiske data
        self.temp_file = NamedTemporaryFile(delete=False, suffix=".csv", mode='w', newline='')
        df = pd.DataFrame({
            'sourceId': ['test_station'] * 24,
            'referenceTimestamp': pd.date_range('2022-01-01', periods=24, freq='MS'),
            'value': np.linspace(50, 100, 24)
        })
        df.to_csv(self.temp_file.name, index=False)
        self.filename = self.temp_file.name

    def tearDown(self):
        # Fjern midlertidig fil
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_predict_from_csv_returns_expected_structure(self):
        forecast_df, historical_df, evaluation_df, mse = predict_from_csv(self.filename, freq='MS', periods=6)

        # Sjekk forecast-df
        self.assertEqual(len(forecast_df), 6)
        self.assertIn('timestamp', forecast_df.columns)
        self.assertIn('predicted_value', forecast_df.columns)

        # Sjekk historisk data
        self.assertFalse(historical_df.empty)
        self.assertIn('historical_value', historical_df.columns)
        self.assertIn('referenceTimestamp', historical_df.columns)

        # Sjekk evalueringsdata
        self.assertIn('actual_value', evaluation_df.columns)
        self.assertIn('predicted_value', evaluation_df.columns)

        # Sjekk at MSE er et tall
        self.assertIsInstance(mse, float)
        self.assertGreaterEqual(mse, 0)

if __name__ == '__main__':
    unittest.main()
