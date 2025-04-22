# README for `miljodataAnalyse`

Denne mappen inneholder kildekoden for prosjektet `miljodataAnalyse`. Koden er strukturert i moduler som håndterer ulike oppgaver som datainnhenting, prosessering, prediksjon og visualisering.

## Moduler

### 1. `API/weather_oslo_met.py`
- **Beskrivelse**: Henter værdata fra Frost API og lagrer dem som CSV.
- **Hovedfunksjonalitet**:
  - `FrostDataFetcher`: Klasse som håndterer hele prosessen fra datainnhenting til lagring.
    - `fetch_data()`: Henter data fra Frost API.
    - `process_data(data)`: Tilpasser dataene til et bedre format.
    - `save_to_csv(df)`: Lagrer dataene som CSV.
    - `run()`: Kjører hele prosessen.
- **Bruk**: Kan brukes til å hente værdata for spesifikke stasjoner og tidsperioder.

### 2. `API/Get_locations.py`
- **Beskrivelse**: Henter værstasjoner fra Frost API basert på geografiske områder.
- **Hovedfunksjonalitet**:
  - `fetch_all_stations(client_id, save, csv_filename, polygon)`: Henter stasjoner innenfor et spesifisert polygon og lagrer dem som CSV.
- **Bruk**: Brukes til å hente stasjonsdata for ulike fylker i Norge.

### 3. `data_processing.py`
- **Beskrivelse**: Prosesserer værdata for analyse og visualisering.
- **Hovedfunksjonalitet**:
  - `clean_columns(df)`: Rydder opp i kolonner og trekker ut relevante data.
  - `preprocess_dataframe(df)`: Konverterer verdier og tidsstempel, og fjerner ugyldige rader.
  - `remove_outliers(df)`: Fjerner uteliggere basert på Z-score.
  - `resample_and_aggregate(df)`: Resampler data og beholder siste måling per dag.
  - `fill_missing_values(df)`: Fyller manglende verdier med lineær regresjon.
  - `add_station_metadata(df, stationsdata_path)`: Legger til stasjonsmetadata som navn og koordinater.
  - `process_weather_data(df, stationsdata_path)`: Kjører hele prosessen for datarensing og prosessering.
- **Bruk**: Brukes til å klargjøre data for analyse og visualisering.

### 4. `predictions.py`
- **Beskrivelse**: Utfører prediksjoner basert på værdata.
- **Hovedfunksjonalitet**:
  - `read_csv_data(filename)`: Leser og renser data fra CSV.
  - `resample_and_engineer_features(df, freq)`: Resampler data og lager sesongbaserte features.
  - `train_linear_model(df)`: Trener en lineær regresjonsmodell.
  - `create_forecast(model, start_time, last_time, freq, periods, period_len)`: Lager fremtidige prediksjoner.
  - `predict_from_csv(filename, freq, periods)`: Kjører hele prediksjonsprosessen fra CSV.
- **Bruk**: Brukes til å lage fremtidige værprediksjoner basert på historiske data.

### 5. `heatmap_utils.py`
- **Beskrivelse**: Lager heatmaps for værdata.
- **Hovedfunksjonalitet**:
  - `load_data(data_dir)`: Leser inn data fra CSV-filer.
  - `filter_data(df, datatype, selected_date, max_value)`: Filtrerer og skalerer data for visualisering.
  - `interpolate_data(df, grid_res, cutoff_radius_km)`: Interpolerer data over et rutenett.
  - `make_map(df, radius, intensity, threshold)`: Lager et heatmap med pydeck.
  - `plot_legend(min_val, max_val)`: Lager en fargeskala for nedbørverdier.
- **Bruk**: Brukes til å visualisere værdata som heatmaps.

