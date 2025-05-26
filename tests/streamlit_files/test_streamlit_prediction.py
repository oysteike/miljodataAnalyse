import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Legg til src i sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from streamlit_files import streamlit_prediction

class TestStreamlitPrediction(unittest.TestCase):
    @patch('streamlit_files.streamlit_prediction.st')
    @patch('streamlit_files.streamlit_prediction.os')
    @patch('streamlit_files.streamlit_prediction.pd')
    @patch('streamlit_files.streamlit_prediction.np')
    @patch('streamlit_files.streamlit_prediction.go')
    @patch('streamlit_files.streamlit_prediction.predict_from_csv')
    @patch('streamlit_files.streamlit_prediction.r2_score')
    def test_show_runs_without_exception(self, mock_r2, mock_predict, mock_go, mock_np, mock_pd, mock_os, mock_st):
        # Mock filsystem
        mock_os.path.dirname.return_value = '/tmp'
        mock_os.path.abspath.return_value = '/tmp'
        mock_os.path.join.side_effect = lambda *args: '/'.join(args)
        mock_os.listdir.return_value = ['test.csv']

        # Dummy DataFrames for prediksjon
        import pandas as pd
        forecast_df = pd.DataFrame({'timestamp': pd.date_range('2025-01-01', periods=3), 'predicted_value': [1, 2, 3]})
        historical_df = pd.DataFrame({'referenceTimestamp': pd.date_range('2022-01-01', periods=3), 'historical_value': [1, 2, 3]})
        evaluation_df = pd.DataFrame({
            'referenceTimestamp': pd.date_range('2024-01-01', periods=3),
            'actual_value': [1, 2, 3],
            'predicted_value': [1, 2, 3]
        })
        mock_predict.return_value = (forecast_df, historical_df, evaluation_df, 1.0)
        mock_pd.to_datetime.side_effect = lambda x: x
        mock_pd.read_csv.return_value = pd.DataFrame({
            'referenceTimestamp': pd.date_range('2022-01-01', periods=3),
            'value': [1, 2, 3],
            'is_interpolated': [False, True, False]
        })
        mock_st.selectbox.side_effect = ['test.csv', 'MS']
        mock_st.slider.return_value = 12
        mock_st.date_input.return_value = '2022-01-01'
        mock_r2.return_value = 0.9
        mock_np.sqrt.return_value = 1.0

        # Kjør funksjonen og sjekk at ingen exceptions kastes
        try:
            streamlit_prediction.show()
        except Exception as e:
            self.fail(f"show() raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()