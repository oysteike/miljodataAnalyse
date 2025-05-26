import unittest
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))

from processing.correlation_utils import load_data, calculate_correlation

class TestCorrelationUtils(unittest.TestCase):
    def setUp(self):
        # Lag eksempeldata
        self.df = pd.DataFrame({
            'referenceTimestamp': pd.date_range('2020-01-01', periods=3),
            'value_1': [1, 2, 3],
            'value_2': [1, 2, 3]
        })

    def test_calculate_correlation_perfect(self):
        corr = calculate_correlation(self.df)
        self.assertAlmostEqual(corr, 1.0)

    def test_load_data_invalid(self):
        df = load_data('not_a_file.csv', 'not_a_file2.csv')
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()