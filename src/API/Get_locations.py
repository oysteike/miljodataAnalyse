import requests
import pandas as pd

def fetch_all_stations(client_id, save=False, csv_filename="buskerud_stasjoner.csv", polygon = "POLYGON((8.2 59.3, 10.3 59.3, 10.3 61.3, 8.2 61.3, 8.2 59.3))"):
    """
    Henter værstasjoner, med buskerud som standard instilling.
    Args:
        client_id (str): Klient-ID for autentisering.
        save (bool): Om data skal lagres som CSV.
        csv_filename (str): Filnavn for CSV-filen.
        polygon (str): Geometri i WKT-format for å spesifisere området.
    Returnerer en dict: { navn: [source_id, [lon, lat]] }
    Lagrer også en CSV med kolonnene: station_name, source_id, lon, lat
    """
    url = "https://frost.met.no/sources/v0.jsonld"
    
    
    params = {
        "geometry": polygon,
        "types": "SensorSystem"
    }

    response = requests.get(url, params=params, auth=(client_id, ""))
    
    if response.status_code != 200:
        print(f"⚠️  Feil ved henting av stasjoner: {response.status_code}")
        print(response.text)
        return {}

    data = response.json().get("data", [])
    rows = []
    station_dict = {}

    for entry in data:
        name = entry.get("name")
        source_id = entry.get("id")
        coords = entry.get("geometry", {}).get("coordinates")
        
        if name and source_id and coords and len(coords) == 2:
            lon, lat = coords
            station_dict[name] = [source_id, coords]
            rows.append({
                "station_name": name,
                "source_id": source_id,
                "lon": lon,
                "lat": lat
            })
    if save:
        # Lag DataFrame og lagre som CSV
        df = pd.DataFrame(rows)
        file_path = "data/" + csv_filename 
        df.to_csv(file_path, index=False, encoding='utf-8')

        print(f"Stasjoner lagret som CSV: {file_path}")

    return station_dict
