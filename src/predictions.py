import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_from_csv(filepath, freq, periods):
    # Leser hele CSV-filen (forventer at den ikke har header)
    df_raw = pd.read_csv(filepath)

    # Sjekker at det er minst 11 kolonner (for å hente ut 'value' og 'referenceTimestamp')
    if df_raw.shape[1] < 11:
        raise ValueError("CSV-filen har for få kolonner.")

    # Setter navn på kolonnene etter Frost API-struktur + eventuelle ekstra kolonner
    df_raw.columns = (
        ['datatype', 'value', 'unit', 'timeOffset', 'timeResolution',
         'timeSeriesId', 'performanceCategory', 'qualityCode', '..',
         'station', 'referenceTimestamp'] +
        [f'extra_{i}' for i in range(df_raw.shape[1] - 11)]  # Navn til eventuelle overflødige kolonner
    )

    # Beholder kun kolonnene vi trenger: tidspunkt og måleverdi
    df = df_raw[['referenceTimestamp', 'value']].copy()

    # Konverterer til datetime og numerisk format, eventuelle ugyldige verdier blir NaT/NaN
    df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'].astype(str).str[:10], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Fjerner rader med manglende eller ugyldige verdier
    df = df.dropna()

    # Stopper hvis vi står igjen med tomt datasett
    if df.empty:
        raise ValueError("Ingen gyldige målinger etter rensing.")

    # Setter tidspunkt som indeks og resampler etter ønsket frekvens (f.eks. ukentlig/månedlig)
    df = df.set_index('referenceTimestamp').resample(freq).mean().dropna()

    if df.empty:
        raise ValueError("Ingen data igjen etter resampling.")

    # Lager en numerisk tidsvariabel: sekunder fra første måling
    start_time = df.index.min()
    df['time_numeric'] = (df.index - start_time).total_seconds()

    # Bestemmer antall perioder i en sesong (måned = 12, uke = 52)
    period_len = {'MS': 12, 'W': 52}.get(freq)
    if not period_len:
        raise ValueError("Frekvens ikke støttet: bruk 'MS' eller 'W'.")

    # Legger til sesongvariabel basert på måned eller ukenummer
    df['season'] = df.index.month if freq == 'MS' else df.index.isocalendar().week

    # Lager sesongkomponenter (sinus og cosinus) for å fange periodiske mønstre
    df['season_sin'] = np.sin(2 * np.pi * df['season'] / period_len)
    df['season_cos'] = np.cos(2 * np.pi * df['season'] / period_len)

    # Inputvariabler til modellen (tid og sesong), og måleverdien som respons
    X = df[['time_numeric', 'season_sin', 'season_cos']]
    y = df['value']

    # Sjekker at vi har nok data til å trene modellen
    if X.empty or y.empty:
        raise ValueError("Ikke nok data til modelltrening.")

    # Trener lineær regresjonsmodell på dataene
    model = LinearRegression().fit(X, y)

    # Lager fremtidige datoer basert på siste måling
    last_time = df.index.max()
    future_dates = pd.date_range(start=last_time + pd.Timedelta(days=1), periods=periods, freq=freq)

    # Konverterer fremtidige datoer til samme numeriske tidsskala
    future_time_numeric = (future_dates - start_time).total_seconds()

    # Beregner sesongverdier for fremtidige datoer
    future_season = future_dates.month if freq == 'MS' else future_dates.isocalendar().week
    future_sin = np.sin(2 * np.pi * future_season / period_len)
    future_cos = np.cos(2 * np.pi * future_season / period_len)

    # Lager feature-matrisen for fremtidig prediksjon og bruker modellen
    X_future = np.column_stack([future_time_numeric, future_sin, future_cos])
    predicted_values = model.predict(X_future)

    # Setter sammen resultatet i en DataFrame med fremtidige prediksjoner
    forecast_df = pd.DataFrame({
        'timestamp': future_dates,
        'predicted_value': predicted_values
    })

    # Omdøper verdikolonnen til 'historical_value' og resetter indeksen for plotting
    historical_df = df.rename(columns={'value': 'historical_value'}).reset_index()

    return forecast_df, historical_df
