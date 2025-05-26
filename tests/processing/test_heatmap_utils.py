import unittest
import pandas as pd
import numpy as np
from io import BytesIO
import pydeck as pdk
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src', 'processing')))

from heatmap_utils import (
    load_data, filter_data, interpolate_data,
    make_map, plot_legend,
)

class TestWeatherMappingFunctions(unittest.TestCase):

    def setUp(self):
        # Lag en test-DataFrame
        self.df = pd.DataFrame({
            "referenceTimestamp": pd.to_datetime(["2025-01-15", "2025-01-15", "2025-01-16", "2025-01-17"]),
            "lon": [10.0, 10.1, 10.0, 10.1],
            "lat": [60.0, 60.0, 60.1, 60.1],
            "value": [1.0, 2.0, 3.0, 4.0],
            "datatype": ["nedbør", "nedbør", "nedbør", "nedbør"]
        })

    def test_filter_data_positive(self):
        # Test at filter_data returnerer riktig antall rader og kolonner
        filtered = filter_data(self.df, "nedbør", "2025-01-15", 20)
        self.assertEqual(len(filtered), 2)
        self.assertIn("plot_value", filtered.columns)

        filtered = filter_data(self.df, "nedbør", "2025-01-18", 20)
        self.assertEqual(len(filtered), 0)

    def test_interpolate_data(self):
        # Test at interpolate_data returnerer en DataFrame med interpolerte verdier
        df_input = self.df[self.df["datatype"] == "nedbør"]
        df_input = df_input.rename(columns={"value": "plot_value"})
        interp = interpolate_data(df_input, cutoff_km=100)
        self.assertGreater(len(interp), 4) # Sjekk at det er flere rader enn input
        self.assertFalse(interp.empty) 
        self.assertIn("plot_value", interp.columns) 

    def test_interpolate_data_too_few_points(self):
        # Test at interpolate_data returnerer en tom DataFrame når det er for få punkter
        df_few = self.df.iloc[:2].copy()
        df_few["plot_value"] = df_few["value"]
        result = interpolate_data(df_few, 100)
        self.assertTrue(result.empty)
        self.assertIsInstance(result, pd.DataFrame)

    def test_interpolate_data_missing_column(self):
        df_missing = self.df.drop(columns=["lon"])  # Mangler nødvendig kolonne
        df_missing["plot_value"] = df_missing["value"]
        result = interpolate_data(df_missing, 100)
        self.assertTrue(result.empty)
        self.assertIsInstance(result, pd.DataFrame)

    def test_make_map_returns_deck(self):
        df_input = self.df[self.df["datatype"] == "nedbør"]
        df_input["plot_value"] = df_input["value"]
        deck = make_map(df_input, radius=10, intensity=1, threshold=0.1)
        self.assertIsInstance(deck, pdk.Deck)

    def test_plot_legend_returns_bytesio(self):
        # Test at plot_legend returnerer en BytesIO-objekt
        result = plot_legend(0, 100, datatype="nedbør")
        self.assertIsInstance(result, BytesIO)
        self.assertGreater(result.getbuffer().nbytes, 0)

if __name__ == "__main__":
    unittest.main()
