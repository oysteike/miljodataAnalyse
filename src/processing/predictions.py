import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def read_csv_data(filename):
    """
    Leser inn data fra en CSV-fil og returnerer en DataFrame.
    Fjerner rader med manglende 'sourceId' og konverterer tidsstempel og verdier til riktige typer.
    """
    try:
        df = pd.read_csv(filename)
        df = df[df['sourceId'].notna()]
        df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df[df['value'].notna() & df['referenceTimestamp'].notna()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Filen '{filename}' ble ikke funnet.")
    except Exception as e:
        raise ValueError(f"Kunne ikke lese og tolke data fra '{filename}': {e}")


def resample_and_engineer_features(df, freq):
    """
    Resamplerer DataFrame til ønsket frekvens og lager tidsrelaterte funksjoner.
    Frekvensen kan være 'MS' (månedlig start) eller 'W' (ukentlig).
    """
    if df.empty:
        raise ValueError("DataFrame er tom – kan ikke lage features.")

    try:
        df = df.set_index('referenceTimestamp').resample(freq)['value'].mean().to_frame()

        start_time = df.index.min()
        df.index = df.index.tz_localize(None)
        start_time = start_time.tz_localize(None)

        df['time_numeric'] = (df.index - start_time).total_seconds()

        period_len = {'MS': 12, 'W': 52}[freq]
        df['season'] = df.index.month if freq == 'MS' else df.index.isocalendar().week
        df['season_sin'] = np.sin(2 * np.pi * df['season'] / period_len)
        df['season_cos'] = np.cos(2 * np.pi * df['season'] / period_len)

        return df, start_time, period_len
    except Exception as e:
        raise RuntimeError(f"Feil ved resampling av datasett: {e}")


def train_and_evaluate_model(df):
    """
    Bruker datasettet til å trene en regresjonsmodell og evaluerer egen ytelse.
    """
    if len(df) < 5:
        raise ValueError("Datasettet er for lite til å trene en modell.")
    try:
        X = df[['time_numeric', 'season_sin', 'season_cos']]
        y = df['value']

        # Split: 80 % trening, 20 % testing (ikke stokket – tidsserie)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # Skaler data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Tren modell
        model = LinearRegression().fit(X_train_scaled, y_train)

        # Evaluer modell
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)

        # Lag evalueringstabell
        evaluation_df = pd.DataFrame({
            'referenceTimestamp': df.index[-len(y_test):],
            'actual_value': y_test.values,
            'predicted_value': y_pred
        })

        return model, mse, evaluation_df, scaler
    except Exception as e:
        raise RuntimeError(f"Feil ved trening og evaluering av modellen: {e}")

def create_forecast(model, start_time, last_time, freq, periods, period_len, scaler):
    """
    Oppretter utrykket som skal brukes for å forutsi fremtidige verdier.
    """
    try:
        future_dates = pd.date_range(start=last_time + pd.Timedelta(days=1), periods=periods, freq=freq)
        time_numeric = (future_dates - start_time).total_seconds()
        season = future_dates.month if freq == 'MS' else future_dates.isocalendar().week
        season_sin = np.sin(2 * np.pi * season / period_len)
        season_cos = np.cos(2 * np.pi * season / period_len)

        X_future = np.column_stack([time_numeric, season_sin, season_cos])
        X_future_scaled = scaler.transform(X_future)

        predicted_values = model.predict(X_future_scaled)

        return pd.DataFrame({
            'timestamp': future_dates,
            'predicted_value': predicted_values
        })
    except Exception as e:
        raise RuntimeError(f"Feil ved prediksjon av fremtidige verdier: {e}")


def predict_from_csv(filename, freq, periods):
    """
    Kjører alle funksjonene.
    """
    df = read_csv_data(filename)
    df, start_time, period_len = resample_and_engineer_features(df, freq)
    model, mse, evaluation_df, scaler = train_and_evaluate_model(df)
    forecast_df = create_forecast(model, start_time, df.index.max(), freq, periods, period_len, scaler)


    historical_df = df.rename(columns={'value': 'historical_value'}).reset_index()

    return forecast_df, historical_df, evaluation_df, mse
