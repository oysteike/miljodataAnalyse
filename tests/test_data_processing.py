import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
from data_processing import clean_columns, preprocess_dataframe, remove_outliers, resample_and_aggregate, fill_missing_values, add_station_metadata

import unittest
from io import StringIO
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import isodate


class TestWeatherDataProcessor(unittest.TestCase):

    def test_clean_columns(self):
        # Opprett en test dataframe
        data = {
            'sourceId': ['id1', 'id2'],
            'referenceTime': ['2022-01-01T00:00:00', '2022-01-02T00:00:00'],
            'observations': [
                [
                    {'timeOffset': 'PT1H', 'elementId': 'temp', 'value': 10, 'unit': 'C'},
                    {'timeOffset': 'PT2H', 'elementId': 'temp', 'value': 12, 'unit': 'C'}
                ],
                [
                    {'timeOffset': 'PT1H', 'elementId': 'temp', 'value': 15, 'unit': 'C'},
                    {'timeOffset': 'PT2H', 'elementId': 'temp', 'value': 18, 'unit': 'C'}
                ]
            ]
        }
        df = pd.DataFrame(data)

        # Kjør funksjonen
        result = clean_columns(df)

        # Sjekk at resultatet er korrekt
        self.assertEqual(len(result), 4)
        self.assertEqual(result['sourceId'].nunique(), 2)
        self.assertEqual(result['datatype'].nunique(), 1)
        self.assertEqual(result['unit'].nunique(), 1)

    def test_preprocess_dataframe(self):
        # Opprett en test dataframe
        data = {
            'sourceId': ['id1', 'id2'],
            'referenceTimestamp': ['2022-01-01T00:00:00', '2022-01-02T00:00:00'],
            'datatype': ['temp', 'temp'],
            'value': ['10', '15'],
            'unit': ['C', 'C']
        }
        df = pd.DataFrame(data)

        # Kjør funksjonen
        result = preprocess_dataframe(df)

        # Sjekk at resultatet er korrekt
        self.assertEqual(len(result), 2)
        self.assertEqual(result['value'].dtype, 'int64')

    def test_remove_outliers(self):
    # Create test data
        data = {
        'sourceId': ['A', 'A', 'A'],
        'referenceTimestamp': ['2022-01-01T00:00:00', '2022-01-01T00:00:00', '2022-01-01T00:00:00'],
        'datatype': ['temperature', 'temperature', 'temperature'],
        'value': [10,20, np.nan],
        'unit': ['°C', '°C', '°C']
        }
        df = pd.DataFrame(data)

        # Kjør funksjonen
        df = remove_outliers(df)

        # Sjekk resultatet
        self.assertTrue(df['value'].isna().any())

    def test_resample_and_aggregate(self):
        # Create test data
        data = {
        'sourceId': ['A', 'A', 'A'],
        'referenceTimestamp': ['2022-01-01T00:00:00', '2022-01-01T01:00:00', '2022-01-02T00:00:00'],
        'datatype': ['temperature', 'temperature', 'temperature'],
        'value': [10,20,30],
        'unit': ['°C', '°C', '°C']
        }
        df = pd.DataFrame(data)

        # Kjør funksjonen
        df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp']) # Konverter til datetime
        df = resample_and_aggregate(df)

        # Sjekk resultatet
        self.assertEqual(df.shape[0],2)

    def test_fill_missing_values(self):
        # Create test data
        data = {
        'sourceId': ['A', 'A'],
        'referenceTimestamp': [pd.Timestamp('2022-01-01 00:00:00'), pd.Timestamp('2022-01-02 00:00:00')],
        'datatype': ['temperature', 'temperature'],
        'value': [10, np.nan],
        'unit': ['°C', '°C']
        }
        df = pd.DataFrame(data)

        # Kjør funksjonen
        df = fill_missing_values(df)

        # Sjekk resultatet
        self.assertFalse(df['value'].isna().any())

    def test_add_station_metadata(self):
        # Opprett en test dataframe
        data = {
            'sourceId': ['id1', 'id1'],
            'referenceTimestamp': ['2022-01-01T00:00:00', '2022-01-01T12:00:00'],
            'datatype': ['temp', 'temp'],
            'value': [10, 12],
            'unit': ['C', 'C']
        }
        df = pd.DataFrame(data)

        # Opprett en test metadata dataframe
        metadata_data = {
            'source_id': ['id1'],
            'station_name': ['Stasjon 1'],
            'lon': [10.0],
            'lat': [60.0]
        }
        metadata = pd.DataFrame(metadata_data)

        # Kjør funksjonen
        result = add_station_metadata(df, 'metadata.csv')
        metadata.to_csv('metadata.csv', index=False)
        result = add_station_metadata(df, 'metadata.csv')

        # Sjekk at resultatet er korrekt
        self.assertEqual(len(result), 2)
        self.assertEqual(result['station_name'].nunique(), 1)
        self.assertEqual(result['lon'].nunique(), 1)
        self.assertEqual(result['lat'].nunique(), 1)

        # Fjern metadata filen
        import os
        os.remove('metadata.csv')

if __name__ == '__main__':
    unittest.main()