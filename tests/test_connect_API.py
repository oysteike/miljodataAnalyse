import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src', 'API')))

from weather_oslo_met import FrostDataFetcher

class TestFrostDataFetcher(unittest.TestCase):
    def setUp(self):
        """
        Initialiserer parametere for testene.
        """
        self.client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
        self.ref_time = "2020-01-01/2020-01-02"
        self.source_id = "SN90450"
        self.element = "sum(precipitation_amount P1D)"
        self.output_filename = "test_data.csv"
        self.stationsdata_path = None

    def test_fetch_data_vellykket(self):
        """
        Tester at data hentes vellykket fra API-et.
        """
        fetcher = FrostDataFetcher(
            self.client_id, 
            self.source_id, 
            self.element, 
            self.ref_time, 
            self.output_filename
        )
        data = fetcher.fetch_data()
        self.assertIsNotNone(data, "Data ble ikke hentet vellykket")

    def test_fetch_data_feil(self):
        """
        Tester at feil håndteres korrekt når ugyldig client_id brukes.
        """
        fetcher = FrostDataFetcher(
            "ugyldig_client_id", 
            self.source_id, 
            self.element, 
            self.ref_time, 
            self.output_filename
        )
        data = fetcher.fetch_data()
        self.assertIsNone(data, "Data skulle ikke blitt hentet med ugyldig client_id")

    def test_process_data_vellykket(self):
        """
        Tester at data behandles korrekt.
        """
        fetcher = FrostDataFetcher(
            self.client_id, 
            self.source_id, 
            self.element, 
            self.ref_time, 
            self.output_filename
        )
        data = fetcher.fetch_data()
        if data:
            df = fetcher.process_data(data)
            self.assertIsNotNone(df, "DataFrame ble ikke opprettet")
        else:
            self.fail("Ingen data å behandle")

    def test_save_to_csv_vellykket(self):
        """
        Tester at data lagres som CSV uten feil.
        """
        fetcher = FrostDataFetcher(
            self.client_id, 
            self.source_id, 
            self.element, 
            self.ref_time, 
            self.output_filename
        )
        data = fetcher.fetch_data()
        if data:
            df = fetcher.process_data(data)
            if df is not None:
                try:
                    fetcher.save_to_csv(df)
                    output_path = os.path.join(os.getcwd(), "data", self.output_filename)
                    self.assertTrue(os.path.exists(output_path), "CSV-filen ble ikke lagret")
                finally:
                    if os.path.exists(output_path):
                        os.remove(output_path)  # Rydd opp etter testen
            else:
                self.fail("DataFrame ble ikke opprettet")
        else:
            self.fail("Ingen data å lagre")

if __name__ == "__main__":
    unittest.main()
