import ast
import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression


def csv_reader(filename, datatyper, stationsdata_path=False):
    """
    Leser en CSV-fil og returnerer en pandas DataFrame i et oversiktlig format.
    Fjerner store avvik ved hjelp av Z-score og fyller inn manglende verdier ved hjelp av lineær regresjon.
    
    Args:
        filename (str): Filnavnet til CSV-filen som skal leses.
        datatyper (list): Liste over datatyper som skal behandles.
        metadata_path (str): Sti til metadatafilen (valgfritt).
    
    Returns:
        pd.DataFrame: En DataFrame med kolonnene ['referenceTimestamp', 'datatype', 'value', 'unit', 'station'].
        dersom stationsdata_path (fil med værstasjonenes navn og posisjon) er spesifisert, vil den legge til kolonnene ['station_name', 'lon', 'lat'].
    """
    # Definer forventede kolonner i CSV-filen
    expected_columns = ['datatype', 'value', 'unit', 'timeOffset', 'timeResolution', 
                        'timeSeriesId', 'performanceCategory', 'qualityCode', '..', 
                        'station', 'referenceTimestamp']
    
    # Les CSV-filen og ignorer eventuelle ekstra kolonner
    df = pd.read_csv(filename, usecols=range(len(expected_columns)), header=None, names=expected_columns, dtype={'referenceTimestamp': str})
    
    # Sjekk at nødvendige kolonner finnes i DataFrame
    if not set(expected_columns).issubset(df.columns):
        raise ValueError("CSV-filen har ikke forventede kolonner: 'datatype', 'value', 'unit', 'timeOffset', 'timeResolution', 'timeSeriesId', 'performanceCategory', 'qualityCode', '..', 'station', 'referenceTimestamp'")
    
    # Konverter 'value' til numerisk datatype (håndterer eventuelle feilverdier)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Konverter 'referenceTimestamp' til datetime-format
    df['referenceTimestamp'] = pd.to_datetime(df['referenceTimestamp'], errors='coerce')
    
    # Fjern rader med ugyldige tidsstempler
    df = df.dropna(subset=['referenceTimestamp'])
    
    # Fjern store avvik ved hjelp av Z-score
    df['value'] = df.groupby('datatype')['value'].transform(
        lambda x: x.where(np.abs(zscore(x)) < 3)
    )
    
     # Sorter data etter tid
    df = df.sort_values('referenceTimestamp')

   # Sett referenceTimestamp som indeks
    df = df.set_index('referenceTimestamp')

    # Gruppér dataene etter dato og datatype, og summer verdiene fra samme dag
    df = df.resample('D').agg({
        'datatype': 'first',
        'value': 'sum',  # Summer verdiene
        'unit': 'first',  # Behold den første enheten (antar at den er lik for alle rader)
        'station': 'first'  # Behold den første stasjonen (antar at den er lik for alle rader)
    }).reset_index()
    
    # Fyll inn manglende verdier ved hjelp av lineær regresjon
    for datatype in datatyper:
        subset = df[df['datatype'] == datatype].copy()
        subset = subset.sort_values('referenceTimestamp')
        
        # Konverter tid til numerisk verdi for regresjon
        subset['time_numeric'] = (subset['referenceTimestamp'] - subset['referenceTimestamp'].min()).dt.total_seconds()
        
        missing_mask = subset['value'].isna()
        if missing_mask.any() and not subset['value'].isna().all():
            reg = LinearRegression()
            known_x = subset.loc[~missing_mask, 'time_numeric'].values.reshape(-1, 1)
            known_y = subset.loc[~missing_mask, 'value'].values
            reg.fit(known_x, known_y)
            
            pred_x = subset.loc[missing_mask, 'time_numeric'].values.reshape(-1, 1)
            subset.loc[missing_mask, 'value'] = reg.predict(pred_x)
        
        # Oppdater hoved-DataFrame med de utfylte verdiene
        df.update(subset)
    if stationsdata_path:
        try:
            metadata = pd.read_csv(stationsdata_path, dtype={'source_id': str})
            df['station'] = df['station'].astype(str)  # Sørg for samsvarende datatype
            metadata['source_id'] = metadata['source_id'].astype(str)
            
            # Merge på 'station' (målt data) == 'source_id' (metadata)
            df = df.merge(metadata[['source_id', 'station_name', 'lon', 'lat']],
                        how='left',
                        left_on='station',
                        right_on='source_id')
            df = df.drop(columns=['source_id'])  # Fjern duplikatkolonne
        except FileNotFoundError:
            print(f"Advarsel: Fant ikke fil på {stationsdata_path}. Koordinater og stasjonsnavn blir ikke lagt til.")
        return df

        # Returner den formatterte DataFrame
    return df[['referenceTimestamp', 'datatype', 'value', 'unit', 'station']]


def get_values(data, start_time='2015-01-01', end_time='2025-01-01'):
    """
    Henter verdier for en spesifisert datatype innenfor et tidsintervall.
    Args:
        data (pd.DataFrame): Data som inneholder målinger.
        start_time (str): Starttidspunkt i 'YYYY-MM-DD' format.
        end_time (str): Sluttidspunkt i 'YYYY-MM-DD' format.
    Returns:
        list: Liste med verdier for den spesifiserte datatype innenfor tidsintervallet.
    """
    # Konverter start- og sluttidspunkt til datetime
    start_time = pd.to_datetime(start_time, errors='coerce').tz_localize('UTC')
    end_time = pd.to_datetime(end_time, errors='coerce').tz_localize('UTC')

    # Filtrer data innenfor tidsintervallet
    mask = (data['referenceTimestamp'] >= start_time) & (data['referenceTimestamp'] <= end_time)
    filtered_data = data.loc[mask]

    # Hent verdier for den spesifiserte datatype
    values = []
    for _, row in filtered_data.iterrows():
        try:
            value = float(row['value'])
            values.append(value)
        except ValueError:
            pass  # Ignorer ugyldige verdier

    return values


def mean(data, start_time='2015-01-01', end_time='2025-01-01'):
    """
    Beregner gjennomsnittet av verdier for en spesifisert datatype innenfor et tidsintervall.
    Args:
        data (pd:DataFrame): Data som inneholder målinger.
        start_time (str): Starttidspunkt i 'YYYY-MM-DD' format.
        end_time (str): Sluttidspunkt i 'YYYY-MM-DD' format.
    Returns:
        float: Gjennomsnittet av verdiene innenfor tidsintervallet.
    """
    values = get_values(data, start_time, end_time)
    
    return np.mean(values)


def median(data, start_time='2015-01-01', end_time='2025-01-01'):
    """
    Beregner medianen av verdier for en spesifisert datatype innenfor et tidsintervall.
    Args:
        data (pd.DataFrame): Data som inneholder målinger.
        start_time (str): Starttidspunkt i 'YYYY-MM-DD' format.
        end_time (str): Sluttidspunkt i 'YYYY-MM-DD' format.
    Returns:
        float: Medianen av verdiene innenfor tidsintervallet.
    """
    values = get_values(data, start_time, end_time)
    
    return np.median(values)


def standard_deviation(data, start_time='2015-01-01', end_time='2025-01-01'):
    """
    Beregner standardavviket av verdier for en spesifisert datatype innenfor et tidsintervall.
    Args:
        data (pd.DataFrame): Data som inneholder målinger.
        start_time (str): Starttidspunkt i 'YYYY-MM-DD' format.
        end_time (str): Sluttidspunkt i 'YYYY-MM-DD' format.
    Returns:
        float: Standardavviket av verdiene innenfor tidsintervallet.
    """
    values = get_values(data, start_time, end_time)
    
    return np.std(values)