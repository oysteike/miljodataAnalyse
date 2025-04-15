import requests

def fetch_all_locations(client_id):
    """
    Henter og filtrerer lokasjoner i Oslo, Akershus, Buskerud og Østfold.
    Returnerer en dictionary { navn: [lon, lat] }
    """
    client_id = "5b9e3b06-3d3d-4049-9b86-b52c0e8cfb81"

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

    # Hent alle lokasjoner i regionen
    locations_dict = fetch_all_locations(client_id)
    print(locations_dict)