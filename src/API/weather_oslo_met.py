import requests
import pandas as pd
import os
import sys

modul_path = os.path.join(os.getcwd(), "src")
sys.path.append(modul_path)
from data_processing import process_weather_data


"""
This class fetches weather data fra frost.met.no and saves as csv
We mada a class to make it easier to test and ajust the code for reuse
init for all parameters needed
fetch_data to get data from frost.met.no, using requests
process_data to adjust the data to a better format
save_to_csv to save the data as csv with pandas DataFrame
run to run the whole process
"""
class FrostDataFetcher:
    def __init__(self, client_id, source_id, elements, ref_time, output_filename="met_data.csv", stationsdata_path=None):
        """
        All variables expected to pull data from frost.met.no
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
        self.output_filename = output_filename # Filename to save data as csv
        self.stationsdata_path = stationsdata_path # Path to stationsdata.csv, if needed
    
    def fetch_data(self):
        response = requests.get(self.endpoint, self.parameters, auth=(self.client_id, '')) # Pulls data from frost.met.no
        
        if response.status_code == 200: # If the pull is successful
            json_data = response.json() # Convert to json
            print('Data retrieved from frost.met.no!')
            return json_data['data']
        
        else:
            print(f'Error! Returned status code {response.status_code}')
            print(f'Message: {response.json()["error"]["message"]}') # Use built in error message
            print(f'Reason: {response.json()["error"]["reason"]}')
            return None
    
    def process_data(self, data):
        """
        Process the data to a better format
        """
        try:
            df = pd.json_normalize(data)
            #print(df.iloc[1, 2])
            #print(df.head())
            #print(f"Data contains {len(df)} rows and {len(df.columns)} columns.")
            #print(f"Data types:\n{df.dtypes}")
            #print(f"Missing values:\n{df.isnull().sum()}")
        except Exception as e:
            print(f"Error when converting data to DataFrame: {e}")
            return None
        df = process_weather_data(df, self.stationsdata_path) # Call the function to process the data
        return df
    
    def save_to_csv(self, df):
        try:

            output_path = os.path.join(os.getcwd(), "data", self.output_filename)
            df.to_csv(output_path, index=False, encoding="utf-8") # Save as csv with path
            print(f"Data saved as CSV at {output_path}")

        except Exception as e: # If error occurs during saving
            print(f"Error when saving as CSV-file: {e}")
    
    def run(self): # Own method to run the whole process
        data = self.fetch_data()
        if data:
            df = self.process_data(data)
            if df is not None:
                self.save_to_csv(df)
            else:
                print("Error processing data")
        else:
            print("No data to process")


if __name__ == "__main__":
    client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
    ref_time = "2015-01-01/2025-01-01"
    source_id = "SN90450"

    
    fetch1 = FrostDataFetcher(client_id, source_id, 'sum(precipitation_amount P1D)',  '2015-01-01/2025-01-01', "Precipitation_data.csv")
    fetch2 = FrostDataFetcher(client_id, source_id, 'sum(duration_of_sunshine P1D)', '2015-01-01/2025-01-01', "Sunshine_data.csv")
    fetch3 = FrostDataFetcher(client_id, source_id, 'max(surface_air_pressure P1D)', '2015-01-01/2025-01-01', "Pressure_data.csv")
    fetch1.run()
    fetch2.run()
    fetch3.run()
    
    
    
    # Hent alle lokasjoner i regionen
    stations_df = pd.read_csv("data/buskerud_stasjoner.csv", dtype={'source_id': str})

    # Vis antall og spør bruker før videre kjøring
    print(f"Det er funnet følgende antall stasjoner i Buskerud: {len(stations_df)}")
    confirm = input("Vil du hente data for alle disse? (ja/nei): ").strip().lower()
    if confirm != "ja":
        print("Avbrutt av bruker.")
        pass

    else:
        elements = [
            "sum(precipitation_amount P1D)",
            "max(surface_air_pressure P1D)"
        ]
        
        source_id_total = ",".join(stations_df['source_id'].unique().astype(str))

        for element in elements:
            print(f"Henter data for alle stasjoner med element '{element}'")
            fetch = FrostDataFetcher(
                client_id,
                source_id_total,
                element, 
                "2025-01-01/2025-02-01",
                output_filename=f"Jan_{element}_Buskerud.csv",
                stationsdata_path=os.path.join(os.getcwd(), "data", "buskerud_stasjoner.csv") # Path to stationsdata.csv
            )
            fetch.run()
