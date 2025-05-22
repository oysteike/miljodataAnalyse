import os
import pandas as pd
from glob import glob

TARGET_INCREASE = 1.5  # Paris-målet innen 2030

def load_all_temperature_data(directory):
    """
    Leser alle CSV-filer i mappen, beregner månedlig gjennomsnittstemperatur 
    over alle stasjoner, og returnerer DataFrame med månedlige verdier.
    """
    try:
        all_files = glob(os.path.join(directory, "*.csv"))
        df_list = []

        for file in all_files:
            df = pd.read_csv(file)
            df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'])
            monthly = df.groupby(pd.Grouper(key='referenceTimestamp', freq='ME'))['value'].mean().reset_index()
            df_list.append(monthly)

        combined_df = pd.concat(df_list)
        combined_monthly_avg = combined_df.groupby('referenceTimestamp')['value'].mean().reset_index()
        return combined_monthly_avg
    
    except Exception:
        return pd.DataFrame()

def calculate_monthly_anomalies(df):
    """
    Tar inn DataFrame med kolonner 'referenceTimestamp' og 'value',
    beregner månedsvise temperaturavvik i forhold til normalverdier mellom 1990 og 2020.
    """
    normals = {
    1: -4.3, 2: -4.1, 3: -0.6, 4: 3.1, 5: 8.7, 6: 12.5, 7: 14.2, 8: 13.5, 9: 9.7, 10: 5.1, 11: 0.1, 12: -3.1
    }

    df['month_num'] = df['referenceTimestamp'].dt.month
    df['year'] = df['referenceTimestamp'].dt.year
    df['normal'] = df['month_num'].map(normals)
    df['anomaly'] = df['value'] - df['normal']

    return df[['referenceTimestamp', 'year', 'month_num', 'value', 'normal', 'anomaly']]

def assess_annual_progress(monthly_anomalies_df, target=TARGET_INCREASE):
    """
    Beregner årlig gjennomsnittsanomali og vurderer progresjon i forhold til mål.
    """
    annual_anomaly = monthly_anomalies_df.groupby('year')['anomaly'].mean().reset_index()
    latest_year = annual_anomaly['year'].max()
    latest_anomaly = annual_anomaly.loc[annual_anomaly['year'] == latest_year, 'anomaly'].values[0]
    overshoot = latest_anomaly - target

    progress = {
        "latest_year": latest_year,
        "latest_anomaly": latest_anomaly,
        "overshoot": overshoot,
        "on_track": latest_anomaly <= target
    }
    return annual_anomaly, progress

def required_reduction(annual_anomaly_df, target=TARGET_INCREASE):
    """
    Estimerer nødvendig årlig reduksjon i temperaturavvik for å nå målet innen 2030.
    """
    latest_year = annual_anomaly_df['year'].max()
    latest_anomaly = annual_anomaly_df.loc[annual_anomaly_df['year'] == latest_year, 'anomaly'].values[0]
    years_left = 2030 - latest_year
    if years_left <= 0:
        return 0
    reduction_needed = latest_anomaly - target
    if reduction_needed <= 0:
        return 0
    return reduction_needed / years_left

def analyze_temperature_progress(TEMPERATURE_DIR):
    """
    - Last data
    - Beregn månedlige anomalier
    - Vurder progresjon årlig
    - Kalkuler nødvendig reduksjon
    """
    df = load_all_temperature_data(TEMPERATURE_DIR)
    requiered_cols = {'referenceTimestamp', 'value'}
    if not requiered_cols.issubset(df.columns):
        return None, None, None

    monthly_anomalies = calculate_monthly_anomalies(df)
    
    annual_anomaly, progress = assess_annual_progress(monthly_anomalies)
    reduction_per_year = required_reduction(annual_anomaly)

    return monthly_anomalies, progress, reduction_per_year


