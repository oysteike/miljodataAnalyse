import requests
import pandas as pd
import os

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
        self.client_id = client_id
        self.source_id = source_id
        self.elements = elements
        self.ref_time = ref_time

        self.output_filename = output_filename
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.parameters = {
            'sources': self.source_id,
            'elements': elements,
            'referencetime': ref_time,
        }
        self.data_adjusted = []
    
    def fetch_data(self):
        response = requests.get(self.endpoint, self.parameters, auth=(self.client_id, ''))
        
        if response.status_code == 200:
            json_data = response.json()
            print('Data retrieved from frost.met.no!')

            return json_data['data']
        else:
            print(f'Error! Returned status code {response.status_code}')
            print(f'Message: {response.json()["error"]["message"]}')
            print(f'Reason: {response.json()["error"]["reason"]}')
            return None
    
    def process_data(self, data):
        for entry in data:
            source_id = entry.get("sourceId", "N/A")
            ref_time = entry.get("referenceTime", "N/A")
            
            for obs in entry.get("observations", []):
                obs["sourceId"] = source_id
                obs["referenceTime"] = ref_time
                self.data_adjusted.append(obs)
        
    
    def save_to_csv(self):
        try:
            df = pd.json_normalize(self.data_adjusted)
            df.fillna("N/A", inplace=True, downcast="infer")

            output_path = os.path.join(os.getcwd(), "data", self.output_filename)
            df.to_csv(output_path, index=False, encoding="utf-8", header=False)
            print(f"Data saved as CSV at {output_path}")
        except Exception as e:
            print(f"Error when saving as CSV-file: {e}")
    
    def run(self):
        data = self.fetch_data()
        if data:
            self.process_data(data)
            self.save_to_csv()


if __name__ == "__main__":
    client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"
    source_id = "SN90450"

    fetch1 = FrostDataFetcher(client_id, source_id, 'sum(precipitation_amount P1D), sum(duration_of_sunshine P1D)',  '2015-01-01/2025-01-01')
    fetch2 = FrostDataFetcher(client_id, source_id, 'max(surface_air_pressure P1D)', '2015-01-01/2025-01-01', "Pressure_data.csv")
    fetch1.run()


