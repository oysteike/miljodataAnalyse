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
        file_path = "data/" + "Verstasjoner/" + csv_filename 
        df.to_csv(file_path, index=False, encoding='utf-8')

        print(f"Stasjoner lagret som CSV: {file_path}")

    return station_dict

if __name__ == "__main__":
    counties = {
  "Viken": {
    "type": "Polygon",
    "coordinates": [
      [
        [10.0, 59.0],
        [10.5, 59.0],
        [10.5, 59.5],
        [10.0, 59.5],
        [10.0, 59.0]
      ]
    ]
  },
  "Oslo": {
    "type": "Polygon",
    "coordinates": [
      [
        [10.6, 59.8],
        [10.8, 59.8],
        [10.8, 60.0],
        [10.6, 60.0],
        [10.6, 59.8]
      ]
    ]
  },
  "Innlandet": {
    "type": "Polygon",
    "coordinates": [
      [
        [9.0, 60.5],
        [10.0, 60.5],
        [10.0, 61.5],
        [9.0, 61.5],
        [9.0, 60.5]
      ]
    ]
  },
  "Vestfold og Telemark": {
    "type": "Polygon",
    "coordinates": [
      [
        [9.0, 58.5],
        [9.5, 58.5],
        [9.5, 59.0],
        [9.0, 59.0],
        [9.0, 58.5]
      ]
    ]
  },
  "Agder": {
    "type": "Polygon",
    "coordinates": [
      [
        [7.5, 58.0],
        [8.5, 58.0],
        [8.5, 58.5],
        [7.5, 58.5],
        [7.5, 58.0]
      ]
    ]
  },
  "Rogaland": {
    "type": "Polygon",
    "coordinates": [
      [
        [5.5, 58.5],
        [6.5, 58.5],
        [6.5, 59.0],
        [5.5, 59.0],
        [5.5, 58.5]
      ]
    ]
  },
  "Vestland": {
    "type": "Polygon",
    "coordinates": [
      [
        [5.0, 60.0],
        [6.0, 60.0],
        [6.0, 61.0],
        [5.0, 61.0],
        [5.0, 60.0]
      ]
    ]
  },
  "Møre og Romsdal": {
    "type": "Polygon",
    "coordinates": [
      [
        [6.0, 62.0],
        [7.0, 62.0],
        [7.0, 63.0],
        [6.0, 63.0],
        [6.0, 62.0]
      ]
    ]
  },
  "Trøndelag": {
    "type": "Polygon",
    "coordinates": [
      [
        [10.0, 63.0],
        [11.0, 63.0],
        [11.0, 64.0],
        [10.0, 64.0],
        [10.0, 63.0]
      ]
    ]
  },
  "Nordland": {
    "type": "Polygon",
    "coordinates": [
      [
        [13.0, 66.0],
        [14.0, 66.0],
        [14.0, 67.0],
        [13.0, 67.0],
        [13.0, 66.0]
      ]
    ]
  },
  "Troms og Finnmark": {
    "type": "Polygon",
    "coordinates": [
      [
        [20.0, 69.0],
        [21.0, 69.0],
        [21.0, 70.0],
        [20.0, 70.0],
        [20.0, 69.0]
      ]
    ]
  }
}
for county, data in counties.items():
    print(f"Fetching stations for {county}")
    polygon = data["coordinates"][0]
    polygon_str = "POLYGON((" + ", ".join([f"{lon} {lat}" for lon, lat in polygon]) + "))"
    fetch_all_stations("5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81", save=True, csv_filename=f"{county}_stations.csv", polygon=polygon_str)