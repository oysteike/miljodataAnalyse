# MiljodataAnalyse – Moduloversikt

Dette prosjektet består av flere moduler for å hente, prosessere, analysere og visualisere værdata fra frost.met.no og andre kilder. Under følger en oversikt over mapper og tilhørende filer, med en kort forklaring for hver fil.

---

## API

### `weather_oslo_met.py`
Henter værdata fra frost.met.no API, renser dataene og lagrer dem som CSV.

### `Get_locations.py`
Henter alle værstasjoner innenfor et geografisk område (polygon) og lagrer som CSV.

---

## processing

### `transform_data.py`
Metoder for rensing, transformasjon og klargjøring av værdata. Denne skal brukes før CSV lagring

### `temperature_calculations.py`
Beregner månedlige gjennomsnitt, temperaturavvik og progresjon mot klimamål.

### `predictions.py`
Trener og evaluerer prediksjonsmodeller for fremtidige værdata.

### `heatmap_utils.py`
Verktøy for å lage og visualisere interpolerte heatmaps av værdata.

### `correlation_utils.py`
Sammenligner og analyserer korrelasjon mellom to ulike datasett.

---

## streamlit_files

### `streamlit_temperature.py`
Streamlit-app for å vise temperaturutvikling og avvik.

### `streamlit_prediction.py`
Streamlit-app for å vise fremtidsprediksjoner og modellvurdering.

### `streamlit_heatmap.py`
Streamlit-app for å vise interpolerte heatmaps av værdata.

### `streamlit_correlation.py`
Streamlit-app for å sammenligne og analysere korrelasjon mellom to datasett.

---

**Generelt:**  
Alle moduler bruker Pandas for databehandling. Visualisering skjer med Plotly, Matplotlib eller Pydeck. Streamlit brukes for interaktive web-applikasjoner.

