import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Legg til src i sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from streamlit_files import streamlit_heatmap

class TestStreamlitHeatmap(unittest.TestCase):
    @patch('streamlit_files.streamlit_heatmap.st')
    @patch('streamlit_files.streamlit_heatmap.load_data')
    @patch('streamlit_files.streamlit_heatmap.filter_data')
    @patch('streamlit_files.streamlit_heatmap.interpolate_data')
    @patch('streamlit_files.streamlit_heatmap.make_map')
    @patch('streamlit_files.streamlit_heatmap.plot_legend')
    def test_show_runs_without_exception(self, mock_legend, mock_map, mock_interp, mock_filter, mock_load, mock_st):
        # Dummy dataframe
        import pandas as pd
        dummy_df = pd.DataFrame({
            'datatype': ['nedbør', 'nedbør'],
            'referenceTimestamp': ['2025-01-01', '2025-01-02'],
            'value': [10, 20],
            'lat': [60.0, 61.0],
            'lon': [10.0, 11.0]
        })
        mock_load.return_value = dummy_df
        mock_filter.return_value = dummy_df
        mock_interp.return_value = dummy_df
        mock_map.return_value = MagicMock()
        mock_legend.return_value = MagicMock()

        # Mock Streamlit widgets
        mock_st.selectbox.return_value = 'nedbør'
        mock_st.number_input.return_value = 0

        # Kjør funksjonen og sjekk at ingen exceptions kastes
        try:
            streamlit_heatmap.show()
        except Exception as e:
            self.fail(f"show() raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()