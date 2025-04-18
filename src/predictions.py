import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def read_csv_data(filename):
    df = pd.read_csv(filename)
    df = df[df['sourceId'].notna()]
    df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'])
    df['value'] = pd.to_numeric(df['value'])
    return df[df['value'].notna()]

def resample_and_engineer_features(df, freq):
    df = df.set_index('referenceTimestamp').resample(freq)['value'].mean().to_frame()

    start_time = df.index.min()
    # Fjern tidssone fra både start_time og df.index
    df.index = df.index.tz_localize(None)
    start_time = start_time.tz_localize(None)

    df['time_numeric'] = (df.index - start_time).total_seconds()

    period_len = {'MS': 12, 'W': 52}[freq]
    df['season'] = df.index.month if freq == 'MS' else df.index.isocalendar().week
    df['season_sin'] = np.sin(2 * np.pi * df['season'] / period_len)
    df['season_cos'] = np.cos(2 * np.pi * df['season'] / period_len)

    return df, start_time, period_len


def train_linear_model(df):
    X = df[['time_numeric', 'season_sin', 'season_cos']]
    y = df['value']
    model = LinearRegression().fit(X, y)
    return model

def create_forecast(model, start_time, last_time, freq, periods, period_len):
    future_dates = pd.date_range(start=last_time + pd.Timedelta(days=1), periods=periods, freq=freq)
    time_numeric = (future_dates - start_time).total_seconds()
    season = future_dates.month if freq == 'MS' else future_dates.isocalendar().week
    season_sin = np.sin(2 * np.pi * season / period_len)
    season_cos = np.cos(2 * np.pi * season / period_len)

    X_future = np.column_stack([time_numeric, season_sin, season_cos])
    predicted_values = model.predict(X_future)

    return pd.DataFrame({
        'timestamp': future_dates,
        'predicted_value': predicted_values
    })

def predict_from_csv(filename, freq, periods):
    df = read_csv_data(filename)
    df, start_time, period_len = resample_and_engineer_features(df, freq)
    model = train_linear_model(df)
    forecast_df = create_forecast(model, start_time, df.index.max(), freq, periods, period_len)
    historical_df = df.rename(columns={'value': 'historical_value'}).reset_index()
    return forecast_df, historical_df

