import pandas as pd
def csv_to_df(filename):
    """
    Leser en CSV-fil og returnerer en DataFrame.
    Args:
        filename (str): Filbane til CSV-filen.
    Returns:
        pd.DataFrame: DataFrame med data fra CSV-filen.
    """
    df = pd.read_csv(filename, dtype={'referenceTimestamp': str})
    return df

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