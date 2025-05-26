import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Legg til src i sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from streamlit_files import streamlit_temperature

class TestStreamlitTemperature(unittest.TestCase):
    @patch('streamlit_files.streamlit_temperature.st')
    @patch('streamlit_files.streamlit_temperature.px')
    @patch('streamlit_files.streamlit_temperature.analyze_temperature_progress')
    def test_show_runs_without_exception(self, mock_analyze, mock_px, mock_st):
        # Dummy DataFrame og progress
        import pandas as pd
        dummy_df = pd.DataFrame({
            'referenceTimestamp': pd.date_range('2022-01-01', periods=6, freq='M'),
            'anomaly': [0.5, 0.7, 1.0, 1.2, 1.1, 1.3]
        })
        dummy_progress = {
            'latest_year': 2023,
            'latest_anomaly': 1.2,
            'overshoot': -0.3,
            'on_track': True
        }
        dummy_reduction = 0.1

        mock_analyze.return_value = (dummy_df, dummy_progress, dummy_reduction)
        mock_px.scatter.return_value = MagicMock(add_hline=MagicMock(return_value=None))

        # Kjør funksjonen og sjekk at ingen exceptions kastes
        try:
            streamlit_temperature.show()
        except Exception as e:
            self.fail(f"show() raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()