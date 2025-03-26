import requests

class EmissionsData:
    def __init__(self):
        self.url = "https://data.ssb.no/api/v0/no/table/13931/"
        self.data = None

    def fetch_data(self, UtslpKomp=["K11", "K12"], Tid=[str(year) for year in range(1990, 2024) if year != 2013]):
        """
        Henter utslippsdata fra SSB API.
        Her kan UtslpKomp(stoff) velges fra denne lsiten ["A10","K11","K12","K13","K80","K90","K95"] som tilsvarer [CO2, CH4, N20, HFK, PFK, SF6]
        Tid kan være år mellom 1990 og 2024. Standard uten 2013 slik at regresjonsverktøyet vårt blir testet. 
        """
        payload = {
            "query": [
                {"code": "UtslpTilLuft", "selection": {"filter": "vs:UtslpKildeA01", "values": []}},
                {"code": "UtslpEnergivare", "selection": {"filter": "item", "values": ["VT0"]}},
                {"code": "UtslpKomp", "selection": {"filter": "item", "values": UtslpKomp}},
                {"code": "ContentsCode", "selection": {"filter": "item", "values": ["UtslippCO2ekvival", "Utslipp"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": [str(year) for year in range(1990, 2024) if year != 2013]}}
            ],
            "response": {"format": "json"}
        }
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()  # Sjekker for HTTP-feil
            self.data = response.json()
            return self.data
        except requests.exceptions.RequestException as e:
            print(f"Feil ved henting av data: {e}")
            return None

if __name__ == "__main__":
    emissions = EmissionsData()
    data = emissions.fetch_data()
    if data:
        print("Data hentet suksessfullt!")
