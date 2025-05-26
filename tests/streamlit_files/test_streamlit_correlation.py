import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import numpy as np

# Legg til src i sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from streamlit_files import streamlit_correlation

class TestStreamlitCorrelation(unittest.TestCase):

    @patch('streamlit_files.streamlit_correlation.st')
    @patch('streamlit_files.streamlit_correlation.os')
    @patch('streamlit_files.streamlit_correlation.load_data')
    @patch('streamlit_files.streamlit_correlation.calculate_correlation')
    def test_show_runs_without_exception(self, mock_corr, mock_load, mock_os, mock_st):
        # Lag en ekte liten DataFrame som testdata
        dummy_df = pd.DataFrame({
            'referenceTimestamp': pd.date_range(start='2015-01-01', periods=10, freq='D'),
            'value_1': np.random.rand(10),
            'value_2': np.random.rand(10)
        })

        # Mock filesystem
        mock_os.path.dirname.return_value = '/tmp'
        mock_os.path.abspath.return_value = '/tmp'
        mock_os.path.join.side_effect = lambda *args: '/'.join(args)
        mock_os.listdir.return_value = ['file1.csv', 'file2.csv']

        # Mock data og korrelasjon
        mock_load.return_value = dummy_df
        mock_corr.return_value = 0.75

        # 🎛 Mock Streamlit widgets
        mock_st.selectbox.side_effect = ['file1.csv', 'file2.csv']
        mock_st.date_input.side_effect = [pd.Timestamp("2015-01-01"), pd.Timestamp("2025-01-01")]

        # 🚀 Kjør funksjonen og bekreft at den ikke kaster feil
        try:
            streamlit_correlation.show()
        except Exception as e:
            self.fail(f"show() raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()
