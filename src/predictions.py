import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from file_processing import csv_reader

def predict_from_csv(filename, freq, periods, target_datatype, datatyper):
    # 1. Hent nested dict fra csv_reader
    data = csv_reader(filename, datatyper)

    # 2. Ekstraher rader for valgt datatype
    rows = []
    for timestamp, målinger in data.items():
        if target_datatype in målinger:
            entry = målinger[target_datatype]
            if isinstance(entry, dict) and 'value' in entry:
                rows.append({
                    'referenceTimestamp': timestamp,
                    'value': entry['value']
                })

    if not rows:
        raise ValueError(f"Ingen målinger funnet for '{target_datatype}'")

    # 3. Lag DataFrame
    df = pd.DataFrame(rows)
    df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna()

    if df.empty:
        raise ValueError("Ingen gyldige verdier etter rensing.")

    # 4. Resample etter frekvens
    df = df.set_index('referenceTimestamp').resample(freq).mean().dropna()
    if df.empty:
        raise ValueError("Ingen data igjen etter resampling.")

    # 5. Lag funksjonsvariabler
    start_time = df.index.min()
    df['time_numeric'] = (df.index - start_time).total_seconds()

    period_len = {'MS': 12, 'W': 52}.get(freq)
    if not period_len:
        raise ValueError("Ugyldig frekvens: bruk 'MS' eller 'W'")

    df['season'] = df.index.month if freq == 'MS' else df.index.isocalendar().week
    df['season_sin'] = np.sin(2 * np.pi * df['season'] / period_len)
    df['season_cos'] = np.cos(2 * np.pi * df['season'] / period_len)

    # 6. Tren modell
    X = df[['time_numeric', 'season_sin', 'season_cos']]
    y = df['value']
    model = LinearRegression().fit(X, y)

    # 7. Lag fremtidige prediksjoner
    last_time = df.index.max()
    future_dates = pd.date_range(start=last_time + pd.Timedelta(days=1), periods=periods, freq=freq)
    future_time_numeric = (future_dates - start_time).total_seconds()
    future_season = future_dates.month if freq == 'MS' else future_dates.isocalendar().week
    future_sin = np.sin(2 * np.pi * future_season / period_len)
    future_cos = np.cos(2 * np.pi * future_season / period_len)

    X_future = np.column_stack([future_time_numeric, future_sin, future_cos])
    predicted_values = model.predict(X_future)

    forecast_df = pd.DataFrame({
        'timestamp': future_dates,
        'predicted_value': predicted_values
    })

    historical_df = df.rename(columns={'value': 'historical_value'}).reset_index()

    return forecast_df, historical_df
