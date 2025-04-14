import unittest
import sys, os
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))

from data_processing import csv_reader
from data_processing import get_values

from io import StringIO


class Test_file_processing(unittest.TestCase):
    def setUp(self):
        # Lag en dummy CSV-streng
        self.csv_data = StringIO(
            "temperature,20,C,,PT1H,1,,0,,station1,2025-01-01T00:00:00Z\n"
            "temperature,21,C,,PT1H,1,,0,,station1,2025-01-01T01:00:00Z\n"
            "temperature,,C,,PT1H,1,,0,,station1,2025-01-02T02:00:00Z\n"
            "temperature,5000,C,,PT1H,1,,0,,station1,2025-01-02T03:00:00Z\n"
            "temperature,15,C,,PT1H,1,,0,,station1,2025-01-03T10:00:00Z\n"
            "temperature, 17,C,,PT1H,1,,0,,station1,2025-01-03T13:00:00Z\n"
            "precipitation_amount,1.0,mm,,PT1H,1,,0,,station1,2025-01-01T00:00:00Z\n"
        )
        
        # Midlertidig fil
        self.temp_filename = "temp_test.csv"
        with open(self.temp_filename, 'w') as f:
            f.write(self.csv_data.getvalue())

        self.mock_data = pd.DataFrame({
            'referenceTimestamp': pd.to_datetime([
            '2025-01-01T00:00:00Z', '2025-01-01T12:00:00Z', '2025-01-02T00:00:00Z'
            ]),
            'datatype': ['temperature', 'temperature', 'temperature'],
            'value': [20.0, 15.0, 21.0],
            'unit': ['C', 'C', 'C'],
            'station': ['Station1', 'Station1', 'Station1']
            })

    def tearDown(self):
        # Slett midlertidig fil
        os.remove(self.temp_filename)

    def test_csv_reader_basic_functionality(self):
        datatyper = ['temperature', 'precipitation_amount']
        result = csv_reader(self.temp_filename, datatyper)

        # Sjekk at resultatet er en DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        #Sjekk at kolonnene er som forventet
        expected_columns = ['referenceTimestamp', 'datatype', 'value', 'unit', 'station']
        self.assertTrue(all(col in result.columns for col in expected_columns))

        # Sjekk at det er ingen NaN-verdier i 'value' kolonnen
        self.assertFalse(result['value'].isnull().any())

        # Sjekk at det det er daglige verdier
        self.assertEqual(result['referenceTimestamp'].dt.date.nunique(), len(result))

        # Sjekk at 'datatype' kolonnen inneholder de forventede datatypene
        expected_datatypes = ['temperature', 'precipitation_amount']
        self.assertTrue(all(dt in expected_datatypes for dt in result['datatype'].unique()))

        # Sjekk at stort avvik er fjernet
        self.assertTrue((result['value'] < 1000).all())

        
    def test_get_values_within_range(self):

        start_time = "2025-01-01"
        end_time = "2025-01-03"

        result = get_values(self.mock_data, start_time=start_time, end_time=end_time)
        
        self.assertIn(20.0, result)
        self.assertIn(21.0, result)
        self.assertNotIn(10.0, result)


    def test_get_values_outside_range(self):

        result = get_values(self.mock_data, start_time="2025-01-01", end_time="2025-01-02")
        self.assertEqual(result, [20.0,15.0])



if __name__ == '__main__':
    unittest.main()