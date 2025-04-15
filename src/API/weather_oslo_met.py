import requests
import pandas as pd
import os
import json

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
    def __init__(self, client_id, source_id, elements, ref_time, output_filename="met_data.csv"):
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
        self.data_adjusted = [] # List to store adjusted data
    
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
        for entry in data:
            source_id = entry.get("sourceId", "N/A") # If sourceId is not found, set to "N/A"
            ref_time = entry.get("referenceTime", "N/A")
            
            for obs in entry.get("observations", []): 
                obs["sourceId"] = source_id # Set value for sourceId in observations
                obs["referenceTime"] = ref_time # Set value for referenceTime in observations
                self.data_adjusted.append(obs) # Appends only the observations to the list
        
    
    def save_to_csv(self):
        try:
            df = pd.json_normalize(self.data_adjusted)
            df.fillna("N/A", inplace=True, downcast="infer") # Fill all NaN values with "N/A"
            output_path = os.path.join(os.getcwd(), "data", self.output_filename)
            df.to_csv(output_path, index=False, encoding="utf-8", header=False) # Save as csv with path
            print(f"Data saved as CSV at {output_path}")

        except Exception as e: # If error occurs during saving
            print(f"Error when saving as CSV-file: {e}")
    
    def run(self): # Own method to run the whole process
        data = self.fetch_data()
        if data:
            self.process_data(data)
            self.save_to_csv()
        else:
            print("No data to process")


def fetch_all_locations(client_id):
    """
    Henter og filtrerer lokasjoner i Oslo, Akershus, Buskerud og Østfold.
    Returnerer en dictionary { navn: [lon, lat] }
    """
    bounds = {
        "min_lat": 58.9,
        "max_lat": 61.0,
        "min_lon": 8.2,
        "max_lon": 11.5,
    }
    url = 'https://frost.met.no/sources/v0.jsonld'
    response = requests.get(url, auth=(client_id, ''))
    if response.status_code != 200:
        print(f"Feil ved henting av lokasjoner: {response.status_code}")
        return {}

    data = response.json().get("data", [])
    locations = {}
    for loc in data:
        geometry = loc.get("geometry")
        coords = geometry.get("coordinates") if geometry else None
        if coords and len(coords) == 2:
            lon, lat = coords
            if bounds["min_lat"] <= lat <= bounds["max_lat"] and bounds["min_lon"] <= lon <= bounds["max_lon"]:
                locations[loc.get("name", "Ukjent")] = coords
    return locations

if __name__ == "__main__":
    client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
    ref_time = "2015-01-01/2025-01-01"

    """
    
    """

    # Hent alle lokasjoner i regionen
    locations_dict = fetch_all_locations(client_id)

    # Vis antall og spør bruker før videre kjøring
    print(f"\n🔎 Fant {len(locations_dict)} værstasjoner i Oslo, Akershus, Buskerud og Østfold.")
    confirm = input("Vil du hente data for alle disse? (ja/nei): ").strip().lower()
    if confirm != "ja":
        print("Avbrutt av bruker.")
        exit()

    # For hver lokasjon: hent data og lagre som CSV
    for name, coords in locations_dict.items():
        source_id = f"SN{name.replace(' ', '')}"  # NB! Du må kanskje bruke faktisk sourceId fra Frost
        print(f"📥 Henter data for: {name} ({source_id})")

        # Hent flere elementer for samme stasjon hvis ønskelig
        fetch = FrostDataFetcher(
            client_id,
            source_id,
            "sum(precipitation_amount P1D)",  # Justér for flere elementer hvis du ønsker
            ref_time,
            output_filename=f"{name.replace(' ', '_')}_precip.csv"
        )
        fetch.run()