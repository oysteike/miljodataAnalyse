import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import isodate

"""
Denne metoden renser og prosesserer værdata fra frost.met.no.
Dette er for å forbrede dataene for lagring i csv og videre analyse.
"""

def clean_columns(df):
    """
    Ekspanderer observations-kolonnen og trekker ut relevante felter.
    """
    rows = []
    for _, row in df.iterrows():
        source_id = row['sourceId']
        ref_time = pd.to_datetime(row['referenceTime'])
        for obs in row['observations']:
            time_offset = isodate.parse_duration(obs.get('timeOffset', 'PT0H'))
            adj_time = ref_time + timedelta(seconds=time_offset.total_seconds())
            rows.append({
                'sourceId': source_id,
                'referenceTimestamp': adj_time,
                'datatype': obs['elementId'],
                'value': obs['value'],
                'unit': obs['unit'],
            })
    return pd.DataFrame(rows)

def preprocess_dataframe(df):
    """
    Konverterer verdier og tidsstempel, fjerner ugyldige rader.
    """
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'], errors='coerce')
    df = df.dropna(subset=['referenceTimestamp'])
    return df

def remove_outliers(df):
    """
    Fjerner outliers med Z-score.
    """
    df['value'] = df.groupby('datatype')['value'].transform(
        lambda x: x.where(np.abs(zscore(x.dropna())) < 3, np.nan)
    )
    return df

def resample_and_aggregate(df):
    """
    Beholder siste måling per dag og stasjon.
    """
    df = df.sort_values('referenceTimestamp')
    df['date'] = df['referenceTimestamp'].dt.floor('D')
    df = df.groupby(['date', 'sourceId']).tail(1)
    df = df.drop(columns=['date'])
    return df

def fill_missing_values(df):
    """
    Fyller manglende verdier med lineær regresjon per datatype.
    """
    for datatype in df['datatype'].unique():
        subset = df[df['datatype'] == datatype].copy()
        if subset.empty:
            continue

        subset = subset.sort_values('referenceTimestamp')
        subset['time_numeric'] = (subset['referenceTimestamp'] - subset['referenceTimestamp'].min()).dt.total_seconds()

        missing_mask = subset['value'].isna()
        if missing_mask.any() and not subset['value'].isna().all():
            reg = LinearRegression()
            known_x = subset.loc[~missing_mask, 'time_numeric'].values.reshape(-1, 1)
            known_y = subset.loc[~missing_mask, 'value'].values
            reg.fit(known_x, known_y)

            pred_x = subset.loc[missing_mask, 'time_numeric'].values.reshape(-1, 1)
            subset.loc[missing_mask, 'value'] = reg.predict(pred_x)

        df.update(subset.drop(columns=['time_numeric']))
    return df

def add_station_metadata(df, stationsdata_path):
    """
    Legger til stasjonsnavn og koordinater hvis metadata er tilgjengelig.
    """
    try:
        metadata = pd.read_csv(stationsdata_path, dtype={'source_id': str})
        df['sourceId'] = df['sourceId'].astype(str).str.split(':').str[0] # Fjerner spesikikkasjon av hvilke måleinstrument på værstasjonen
        metadata['source_id'] = metadata['source_id'].astype(str)

        df = df.merge(metadata[['source_id', 'station_name', 'lon', 'lat']],
                      how='left',
                      left_on='sourceId',
                      right_on='source_id')
        df = df.drop(columns=['source_id'])
    except FileNotFoundError:
        print(f"Advarsel: Fant ikke fil på {stationsdata_path}. Koordinater og stasjonsnavn blir ikke lagt til.")
    return df

def process_weather_data(df, stationsdata_path=None):
    """
    Hovedprosess som kjører hele rensingen og prosesseringen.
    """
    df = clean_columns(df)
    df = preprocess_dataframe(df)
    df = remove_outliers(df)
    df = resample_and_aggregate(df)
    df = fill_missing_values(df)

    if stationsdata_path:
        df = add_station_metadata(df, stationsdata_path)

    return df[['sourceId', 'referenceTimestamp', 'datatype', 'value', 'unit', 'lon', 'lat'] if 'lon' in df.columns else ['sourceId', 'referenceTimestamp', 'datatype', 'value', 'unit']]

