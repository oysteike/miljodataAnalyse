import os
from glob import glob
import pandas as pd

# Parisavtalen sitt mål: unngå mer enn 1.5°C temperaturøkning innen 2030
TARGET_INCREASE = 1.5


def load_all_temperature_data(directory):
    """
    Leser alle CSV-filer i gitt mappe og beregner månedlig gjennomsnittstemperatur
    på tvers av alle stasjoner. Returnerer DataFrame med månedlige verdier.
    """
    try:
        all_files = glob(os.path.join(directory, "*.csv"))
        df_list = []

        for file in all_files:
            df = pd.read_csv(file)
            df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'])

            # Beregn gjennomsnitt per måned for denne filen
            monthly = df.groupby(
                pd.Grouper(key='referenceTimestamp', freq='ME')
            )['value'].mean().reset_index()

            df_list.append(monthly)

        # Kombiner alle stasjoner og ta gjennomsnitt på tvers av stasjoner per måned
        combined_df = pd.concat(df_list)
        combined_monthly_avg = combined_df.groupby(
            'referenceTimestamp'
        )['value'].mean().reset_index()

        return combined_monthly_avg

    except Exception:
        return pd.DataFrame()


def calculate_monthly_anomalies(df):
    """
    Tar inn DataFrame med temperaturverdier og beregner temperaturavvik (anomali)
    i forhold til normalverdier for hver måned (1990–2020).
    """
    normals = {
        1: -4.3, 2: -4.1, 3: -0.6, 4: 3.1, 5: 8.7, 6: 12.5,
        7: 14.2, 8: 13.5, 9: 9.7, 10: 5.1, 11: 0.1, 12: -3.1
    }

    df['month_num'] = df['referenceTimestamp'].dt.month
    df['year'] = df['referenceTimestamp'].dt.year
    df['normal'] = df['month_num'].map(normals)
    df['anomaly'] = df['value'] - df['normal']

    return df[['referenceTimestamp', 'year', 'month_num', 'value', 'normal', 'anomaly']]


def assess_annual_progress(monthly_anomalies_df, target=TARGET_INCREASE):
    """
    Vurderer progresjon i forhold til temperaturmålet.
    Returnerer årlige anomalier og et sammendrag av status.
    """
    annual_anomaly = monthly_anomalies_df.groupby('year')['anomaly'].mean().reset_index()

    latest_year = annual_anomaly['year'].max()
    latest_anomaly = annual_anomaly.loc[
        annual_anomaly['year'] == latest_year, 'anomaly'
    ].values[0]

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
    Estimerer nødvendig årlig reduksjon for å nå målet innen 2030.
    Returnerer 0 hvis vi allerede er under målet.
    """
    latest_year = annual_anomaly_df['year'].max()
    latest_anomaly = annual_anomaly_df.loc[
        annual_anomaly_df['year'] == latest_year, 'anomaly'
    ].values[0]

    years_left = 2030 - latest_year

    if years_left <= 0:
        return 0

    reduction_needed = latest_anomaly - target

    if reduction_needed <= 0:
        return 0

    return reduction_needed / years_left


def analyze_temperature_progress(temperature_dir):
    """
    Kjørefunksjon:
    - Leser inn alle temperaturfiler
    - Beregner månedlige temperaturavvik
    - Vurderer progresjon i forhold til Paris-målet
    - Estimerer nødvendig årlig forbedring
    """
    df = load_all_temperature_data(temperature_dir)

    required_cols = {'referenceTimestamp', 'value'}
    if not required_cols.issubset(df.columns):
        return None, None, None

    monthly_anomalies = calculate_monthly_anomalies(df)
    annual_anomaly, progress = assess_annual_progress(monthly_anomalies)
    reduction_per_year = required_reduction(annual_anomaly)

    return monthly_anomalies, progress, reduction_per_year