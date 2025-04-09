import unittest
import sys, os
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))

from file_processing import csv_reader
from file_processing import get_values

from io import StringIO


class Test_file_processing(unittest.TestCase):
    def setUp(self):
        # Lag en dummy CSV-streng
        self.csv_data = StringIO(
            "temperature,20,C,,PT1H,1,,0,,station1,2025-01-01T00:00:00Z\n"
            "temperature,21,C,,PT1H,1,,0,,station1,2025-01-01T01:00:00Z\n"
            "temperature,,C,,PT1H,1,,0,,station1,2025-01-01T02:00:00Z\n"
            "temperature,5000,C,,PT1H,1,,0,,station1,2025-01-01T03:00:00Z\n"
            "precipitation_amount,1.0,mm,,PT1H,1,,0,,station1,2025-01-01T00:00:00Z\n"
            "precipitation_amount,2.0,mm,,PT1H,1,,0,,station1,2025-01-01T00:00:00Z\n"
        )
        
        # Midlertidig fil
        self.temp_filename = "temp_test.csv"
        with open(self.temp_filename, 'w') as f:
            f.write(self.csv_data.getvalue())

    def tearDown(self):
        # Slett midlertidig fil
        os.remove(self.temp_filename)

    def test_csv_reader_basic_functionality(self):
        datatyper = ['temperature', 'precipitation_amount']
        result = csv_reader(self.temp_filename, datatyper)

        # Sjekk at resultatet er en dictionary
        self.assertIsInstance(result, dict)

        # Sjekk at en dato finnes og inneholder riktig datatype
        self.assertIn(date(2025, 1, 1), result)
        self.assertIn('temperature', result[date(2025, 1, 1)])
        self.assertIn('precipitation_amount', result[date(2025, 1, 1)])

        # Sjekk at ekstremverdien ble fjernet (5000)
        self.assertLess(result[date(2025, 1, 1)]['temperature']['value'], 100)

        # Sjekk at manglende verdi ble estimert (skal ikke være None)
        self.assertIsNotNone(result[date(2025, 1, 1)]['temperature']['value'])

        # Sjekk at nedbør er summert (1.0 + 2.0 = 3.0)
        self.assertAlmostEqual(result[date(2025, 1, 1)]['precipitation_amount']['value'], 3.0)
        
    def test_get_values_within_range(self):
        mock_data = {
            "2025-01-01T00:00:00Z": {"temperature": {"value": 20.0},},
            "2025-01-02T00:00:00Z": {"temperature": {"value": 50.0}},
            "2025-01-03T00:00:00Z": {"temperature": {"value": 21.0}},
            "2025-01-04T00:00:00Z": {"temperature": {"value": 10.0}}
        }

        start_time = "2025-01-01"
        end_time = "2025-01-03"

        result = get_values(mock_data, start_time=start_time, end_time=end_time)
        
        print("Filtered result:", result)  
        self.assertIn(20.0, result)
        self.assertIn(21.0, result)
        self.assertIn(50.0, result)
        self.assertNotIn(10.0, result)


    def test_get_values_outside_range(self):
        mock_data = {
            pd.Timestamp("2024-12-31T00:00:00Z"): {
                'temperature': {'value': np.float64(10.0), 'unit': 'C'}
            }
        }
        result = get_values(mock_data, start_time="2025-01-01", end_time="2025-01-02")
        self.assertEqual(result, [])

    def test_get_values_with_invalid_value(self):
        mock_data = {
            pd.Timestamp("2025-01-01T00:00:00Z"): {
                'temperature': {'value': 'not_a_number', 'unit': 'C'}
            }
        }
        result = get_values(mock_data, start_time="2025-01-01", end_time="2025-01-01")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()