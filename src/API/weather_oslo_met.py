import requests
import pandas as pd
import os
import sys

modul_path = os.path.join(os.getcwd(), "src")
sys.path.append(modul_path)
from data_processing import process_weather_data


"""
Denne klassen henter værdata fra frost.met.no og lagrer som csv
Vi laget en klasse for å gjøre det enklere å teste og justere koden for gjenbruk
init for alle nødvendige parametere
fetch_data for å hente data fra frost.met.no, ved bruk av requests
process_data for å tilpasse dataene til et bedre format
save_to_csv for å lagre dataene som csv med pandas DataFrame
run for å kjøre hele prosessen
"""
class FrostDataFetcher:
    def __init__(self, client_id, source_id, elements, ref_time, output_filename="met_data.csv", stationsdata_path=None):
        """
        Alle variabler som trengs for å hente data fra frost.met.no
        """
        self.client_id = client_id
        self.source_id = source_id
        self.elements = elements
        self.ref_time = ref_time
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.parameters = {
            'sources': self.source_id,
            'elements': elements,
            'referencetime': ref_time,
        }
        self.output_filename = output_filename # Filnavn for å lagre data som csv
        self.stationsdata_path = stationsdata_path # Sti til stationsdata.csv, hvis nødvendig
    
    def fetch_data(self):
        response = requests.get(self.endpoint, self.parameters, auth=(self.client_id, '')) # Henter data fra frost.met.no
        
        if response.status_code == 200: # Hvis henting er vellykket
            json_data = response.json() # Konverter til json
            print('Data hentet fra frost.met.no!')
            return json_data['data']
        
        else:
            print(f'Feil! Returnerte statuskode {response.status_code}')
            print(f'Melding: {response.json()["error"]["message"]}') # Bruk innebygd feilmelding
            print(f'Årsak: {response.json()["error"]["reason"]}')
            return None
    
    def process_data(self, data):
        """
        Tilpasser dataene til et bedre format
        """
        try:
            df = pd.json_normalize(data)
            #print(df.iloc[1, 2])
            #print(df.head())
            #print(f"Data inneholder {len(df)} rader og {len(df.columns)} kolonner.")
            #print(f"Datatyper:\n{df.dtypes}")
            #print(f"Manglende verdier:\n{df.isnull().sum()}")
        except Exception as e:
            print(f"Feil ved konvertering av data til DataFrame: {e}")
            return None
        df = process_weather_data(df, self.stationsdata_path) # Kall funksjonen for å behandle dataene
        return df
    
    def save_to_csv(self, df):
        try:

            output_path = os.path.join(os.getcwd(), "data", self.output_filename)
            df.to_csv(output_path, index=False, encoding="utf-8") # Lagre som csv med sti
            print(f"Data lagret som CSV på {output_path}")

        except Exception as e: # Hvis feil oppstår under lagring
            print(f"Feil ved lagring som CSV-fil: {e}")
    
    def run(self): # Egen metode for å kjøre hele prosessen
        data = self.fetch_data()
        if data:
            df = self.process_data(data)
            if df is not None:
                self.save_to_csv(df)
            else:
                print("Feil ved behandling av data")
        else:
            print("Ingen data å behandle")


if __name__ == "__main__":
    client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
    ref_time = "2015-01-01/2025-01-01"
    source_id = "SN90450"

    """
    fetch1 = FrostDataFetcher(client_id, source_id, 'sum(precipitation_amount P1D)',  '2015-01-01/2025-01-01', "Precipitation_data.csv")
    fetch2 = FrostDataFetcher(client_id, source_id, 'sum(duration_of_sunshine P1D)', '2015-01-01/2025-01-01', "Sunshine_data.csv")
    fetch3 = FrostDataFetcher(client_id, source_id, 'max(surface_air_pressure P1D)', '2015-01-01/2025-01-01', "Pressure_data.csv")
    fetch1.run()
    fetch2.run()
    fetch3.run()
    """
    
    for station_name in ['Agder', 'Innlandet', 'Oslo', 'Viken', 'Vestfold og Telemark', 'Møre og Romsdal', 'Nordland', 'Vestland', 'Trøndelag', 'Troms og Finnmark', 'Rogaland']:
        
        # Hent alle lokasjoner i regionen
        stationsdata_path = os.path.join(os.getcwd(), "data", "Verstasjoner", f"{station_name}_stations.csv")
        stations_df = pd.read_csv(stationsdata_path)

        # Vis antall og spør bruker før videre kjøring
        print(f"Det er funnet følgende antall stasjoner i {station_name}: {len(stations_df)}")
        confirm = input("Vil du hente data for alle disse? (ja/nei): ").strip().lower()
        if confirm != "ja":
            print("Avbrutt av bruker.")
            pass

        else:
            elements = [
                "sum(precipitation_amount P1D)",
            ]
            
            source_id_total = ",".join(stations_df['source_id'].unique().astype(str))

            for element in elements:
                print(f"Henter data for alle stasjoner med element '{element}'")
                fetch = FrostDataFetcher(
                    client_id,
                    source_id_total,
                    element, 
                    "2025-01-01/2025-02-01",
                    output_filename=f"Jan_2025/{element}_{station_name}.csv",
                    stationsdata_path=stationsdata_path # Sti til stationsdata.csv
                )
                fetch.run()

