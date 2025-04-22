import unittest
import os
import pandas as pd
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
from predictions import predict_from_csv, read_csv_data, resample_and_engineer_features, train_linear_model, create_forecast

class TestPredictions(unittest.TestCase):
    def setUp(self):
        """
        Initialiserer testdata og parametere.
        """
        self.test_csv = "test_data.csv"
        self.freq = "MS"  # Månedlig frekvens
        self.periods = 12  # Antall perioder for prediksjon

        # Opprett en test CSV-fil
        data = {
            'sourceId': ['SN90450'] * 24,
            'referenceTimestamp': pd.date_range(start="2020-01-01", periods=24, freq="MS"),
            'value': [i for i in range(24)]
        }
        df = pd.DataFrame(data)
        df.to_csv(self.test_csv, index=False)

    def tearDown(self):
        """
        Rydder opp etter testene.
        """
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_read_csv_data(self):
        """
        Tester at CSV-data leses korrekt.
        """
        df = read_csv_data(self.test_csv)
        self.assertFalse(df.empty, "DataFrame er tom")
        self.assertIn('value', df.columns, "Kolonnen 'value' mangler")
        self.assertIn('referenceTimestamp', df.columns, "Kolonnen 'referenceTimestamp' mangler")

    def test_resample_and_engineer_features(self):
        """
        Tester at funksjoner for resampling og feature engineering fungerer.
        """
        df = read_csv_data(self.test_csv)
        df, start_time, period_len = resample_and_engineer_features(df, self.freq)
        self.assertIn('time_numeric', df.columns, "Kolonnen 'time_numeric' mangler")
        self.assertIn('season_sin', df.columns, "Kolonnen 'season_sin' mangler")
        self.assertIn('season_cos', df.columns, "Kolonnen 'season_cos' mangler")

    def test_train_linear_model(self):
        """
        Tester at lineær modell trenes uten feil.
        """
        df = read_csv_data(self.test_csv)
        df, _, _ = resample_and_engineer_features(df, self.freq)
        model = train_linear_model(df)
        self.assertIsNotNone(model, "Modellen ble ikke opprettet")

    def test_create_forecast(self):
        """
        Tester at prediksjoner opprettes korrekt.
        """
        df = read_csv_data(self.test_csv)
        df, start_time, period_len = resample_and_engineer_features(df, self.freq)
        model = train_linear_model(df)
        forecast_df = create_forecast(model, start_time, df.index.max(), self.freq, self.periods, period_len)
        self.assertFalse(forecast_df.empty, "Forecast DataFrame er tom")
        self.assertIn('predicted_value', forecast_df.columns, "Kolonnen 'predicted_value' mangler")

    def test_predict_from_csv(self):
        """
        Tester hele prediksjonsprosessen fra CSV.
        """
        forecast_df, historical_df = predict_from_csv(self.test_csv, self.freq, self.periods)
        self.assertFalse(forecast_df.empty, "Forecast DataFrame er tom")
        self.assertFalse(historical_df.empty, "Historical DataFrame er tom")
        self.assertIn('predicted_value', forecast_df.columns, "Kolonnen 'predicted_value' mangler")
        self.assertIn('historical_value', historical_df.columns, "Kolonnen 'historical_value' mangler")

if __name__ == "__main__":
    unittest.main()
