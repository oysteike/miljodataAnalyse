import unittest
from unittest.mock import patch, Mock
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'API')))
from weather_oslo_met import FrostDataFetcher


class TestFrostDataFetcher(unittest.TestCase):

    def setUp(self):
        self.client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
        self.source_id = "SN12345"
        self.fetcher = FrostDataFetcher(self.client_id, self.source_id, output_filename="test_met_data.csv")

        self.example_data = [
            {
                "sourceId": "SN12345",
                "referenceTime": "2023-01-01T00:00:00Z",
                "observations": [
                    {"elementId": "air_temperature", "value": 5.3, "unit": "C"},
                    {"elementId": "precipitation_amount", "value": None, "unit": "mm"}
                ]
            }
        ]

    @patch('weather_oslo_met.requests.get')
    def test_fetch_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': self.example_data}
        mock_get.return_value = mock_response

        data = self.fetcher.fetch_data()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sourceId"], "SN12345")

    def test_process_data(self):
        self.fetcher.process_data(self.example_data)
        self.assertEqual(len(self.fetcher.data_adjusted), 2)
        self.assertIn("sourceId", self.fetcher.data_adjusted[0])
        self.assertIn("referenceTime", self.fetcher.data_adjusted[0])

    def test_save_to_csv(self):
        self.fetcher.data_adjusted = [
            {"elementId": "air_temperature", "value": 5.3, "unit": "C", "sourceId": "SN12345", "referenceTime": "2023-01-01T00:00:00Z"},
            {"elementId": "precipitation_amount", "value": "N/A", "unit": "mm", "sourceId": "SN12345", "referenceTime": "2023-01-01T00:00:00Z"}
        ]

        self.fetcher.save_to_csv()
        path = os.path.join(os.getcwd(), "data", "test_met_data.csv")
        self.assertTrue(os.path.exists(path))

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("SN12345", content)
            self.assertIn("N/A", content)

        os.remove(path)

    def test_fillna_applied(self):
        self.fetcher.data_adjusted = [
            {"elementId": "precipitation_amount", "value": None, "unit": "mm", "sourceId": "SN12345", "referenceTime": "2023-01-01T00:00:00Z"}
        ]

        self.fetcher.save_to_csv()
        path = os.path.join(os.getcwd(), "data", "test_met_data.csv")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("N/A", content)

        os.remove(path)

    @patch('weather_oslo_met.requests.get')
    def test_full_run(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': self.example_data}
        mock_get.return_value = mock_response

        self.fetcher.run()
        output_path = os.path.join(os.getcwd(), "data", "test_met_data.csv")
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)


if __name__ == '__main__':
    unittest.main()
