import unittest
from unittest.mock import patch, Mock  # Mocking av API-kall, for å unngå nettverkstrafikk
import sys, os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src', 'API')))
from weather_oslo_met import FrostDataFetcher


class TestFrostDataFetcher(unittest.TestCase):

    def test_actual_api_connection(self): # Sjekker om man faktisk kan koble seg til API-en
        fetcher = FrostDataFetcher(self.client_id, "SN18700")
        response = fetcher.fetch_data()
        self.assertIsNotNone(response)
        self.assertIsInstance(response, list)


    def setUp(self):
        # Lager en testinstans av klassen og eksempeldata
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

    @patch('weather_oslo_met.requests.get') # Bruker patch for å mocke requests.get siden man ikke vil teste API-en, men selve koden
    def test_fetch_data_success(self, mock_get):
        # Sjekker at fetch_data() håndterer vellykket API-respons
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': self.example_data}
        mock_get.return_value = mock_response

        data = self.fetcher.fetch_data()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sourceId"], "SN12345")

    def test_process_data(self):
        # Sjekker at process_data() legger inn info i data_adjusted
        self.fetcher.process_data(self.example_data)
        self.assertEqual(len(self.fetcher.data_adjusted), 2)
        self.assertIn("sourceId", self.fetcher.data_adjusted[0])
        self.assertIn("referenceTime", self.fetcher.data_adjusted[0])

    def test_save_to_csv(self):
        # Sjekker at save_to_csv() faktisk lagrer en gyldig fil med riktig innhold
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
        # Sjekker at None-verdier blir erstattet med "N/A" ved lagring
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
        # Sjekker at hele run()-prosessen fungerer med mocket API-respons
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
