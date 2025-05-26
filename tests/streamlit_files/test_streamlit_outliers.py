import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Legg til src i sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from streamlit_files import streamlit_outliers

class TestStreamlitOutliers(unittest.TestCase):
    @patch('streamlit_files.streamlit_outliers.st')
    @patch('streamlit_files.streamlit_outliers.os')
    @patch('streamlit_files.streamlit_outliers.pd')
    def test_show_runs_without_exception(self, mock_pd, mock_os, mock_st):
        # Mock filsystem
        mock_os.path.dirname.return_value = '/tmp'
        mock_os.path.abspath.return_value = '/tmp'
        mock_os.path.join.side_effect = lambda *args: '/'.join(args)
        mock_os.listdir.return_value = ['test.csv']

        # Dummy DataFrame
        import pandas as pd
        dummy_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        mock_pd.read_csv.return_value = dummy_df

        # Mock Streamlit widgets
        mock_st.selectbox.return_value = 'test.csv'

        # Kjør funksjonen og sjekk at ingen exceptions kastes
        try:
            streamlit_outliers.show()
        except Exception as e:
            self.fail(f"show() raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()