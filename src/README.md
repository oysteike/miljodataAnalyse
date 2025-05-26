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
predictions.py
Trener og evaluerer prediksjonsmodeller for fremtidige værdata.

I resample_and_engineer_features brukes sin og cos-funksjoner for å representere årstidsvariasjoner (måneder eller uker) som sykliske variabler. Dette betyr at januar og desember behandles som nærliggende tidspunkter, i motsetning til vanlige numeriske verdier hvor januar (1) og desember (12) har stor avstand. Denne transformasjonen gjør det mulig for modellen å fange opp sesongmønstre som gjentar seg årlig.

I train_and_evaluate_model deles datasettet slik at de første 80 % av observasjonene brukes til trening, og de siste 20 % brukes til å evaluere modellens ytelse. Før treningen standardiseres input-variablene ved hjelp av StandardScaler for å hindre at funksjoner med store verdier, som time_numeric, dominerer regresjonen. Verdiene transformeres etter formelen: z = (x-u)/s. Der u er gjennomsnitt og s er standardavvik. 

### `heatmap_utils.py`
Verktøy for å lage og visualisere interpolerte heatmaps av værdata.

### `correlation_utils.py`
Sammenligner og analyserer korrelasjon mellom to ulike datasett.

---

## streamlit_files
Disse fillene gjør kun visuelle opptreden, plot og streamlit fumkjosner for brukervennlig innteraksjon.

### `streamlit_temperature.py`
Streamlit-app for å vise temperaturutvikling og avvik.

### `streamlit_prediction.py`
Streamlit-app for å vise fremtidsprediksjoner og modellvurdering.

### `streamlit_heatmap.py`
Streamlit-app for å vise interpolerte heatmaps av værdata.

### `streamlit_correlation.py`
Streamlit-app for å sammenligne og analysere korrelasjon mellom to datasett.
Her brukes også standardisering i plottet hvor de to grafene sammenlignes, dette er slik at grafer som pressure og humidity har veldig ulike verdier og må standardiseres for å vise noen visuell sammenheng. 

---

**Generelt:**  
Alle moduler bruker Pandas for databehandling. Visualisering skjer med Plotly, Matplotlib eller Pydeck. Streamlit brukes for interaktive web-applikasjoner.

