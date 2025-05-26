# Testdokumentasjon

Denne mappen inneholder tester for prosjektet `miljodataAnalyse`, skrevet med `unittest`.

## Testfiler

### `test_connect_API.py`
Tester `FrostDataFetcher`-klassen for å hente og lagre værdata fra Frost API.

### `test_predictions.py`
Tester prediksjonsmodulen for å lese data, resample, trene modeller og lage prediksjoner.

### `test_data_processing.py`
Tester funksjoner for databehandling som rensing, resampling og fylling av manglende verdier.

### `processing/test_correlation_utils.py`
Tester funksjoner for å laste inn og sammenligne værdata, samt beregne korrelasjon mellom datasett.

### `processing/test_heatmap_utils.py`
Tester funksjoner for å filtrere, interpolere og visualisere værdata som heatmaps.

### `processing/test_temperature_calculations.py`
Tester funksjoner for å beregne temperaturavvik, årlig progresjon og nødvendig reduksjon i temperatur.

### `processing/test_transform_data.py`
Tester funksjoner for å transformere, rense og berike værdata, inkludert håndtering av stasjonsmetadata.

### `streamlit_files/test_streamlit_correlation.py`
Tester at Streamlit-komponenten for korrelasjonsanalyse kan kjøres uten feil ved hjelp av mocking.

### `streamlit_files/test_streamlit_heatmap.py`
Tester at Streamlit-komponenten for heatmap-visning kan kjøres uten feil ved hjelp av mocking.

### `streamlit_files/test_streamlit_outliers.py`
Tester at Streamlit-komponenten for uteliggervalg og visning kan kjøres uten feil ved hjelp av mocking.

### `streamlit_files/test_streamlit_prediction.py`
Tester at Streamlit-komponenten for fremtidsprediksjon kan kjøres uten feil ved hjelp av mocking.

### `streamlit_files/test_streamlit_temperature.py`
Tester at Streamlit-komponenten for temperaturutvikling og Parisavtalen kan kjøres uten feil ved hjelp av mocking.

## Kjøre tester

1. Installer nødvendige avhengigheter (`pandas`, `numpy`, `scikit-learn`, osv.).
2. Kjør testene med:
   ```bash
   python -m unittest discover -s tests -p "*.py"
   ```
   

Legg til nye tester ved å opprette en fil i `tests/` og følge eksisterende struktur.
