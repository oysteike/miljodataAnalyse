import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
import ast

def csv_reader(filename, datatyper):
    
    
    # Les CSV med korrekt format
    df = pd.read_csv(filename, header=None, names=['datatype', 'value','unit', 'timeOffset', 'timeResolution', 'timeSeriesId', 'performanceCategory', 'qualityCode', '..', 'station', 'referenceTimestamp'])
    

    
    # Sjekk at nødvendige kolonner finnes
    if not {'datatype', 'value','unit', 'timeOffset', 'timeResolution', 'timeSeriesId', 'performanceCategory', 'qualityCode', '..', 'station', 'referenceTimestamp'}.issubset(df.columns):
        raise ValueError("CSV-filen har ikke forventede kolonner: 'datatype', 'value','unit', 'timeOffset', 'timeResolution', 'timeSeriesId', 'performanceCategory', 'qualityCode', '..', 'station', 'referenceTimestamp'")
    
    records = []
    
    for _, row in df.iterrows():
        datatype = row['datatype']
        value = row['value']
        unit = row['unit']
        station = row['station']
        timestamp = (row['referenceTimestamp'])[:10]
        
        
        records.append({
                    'referenceTimestamp': timestamp,
                    'datatype': datatype,
                    'value': value,
                    'unit': unit,
                    'station' : station
                })
    result_df = pd.DataFrame(records)
    if result_df.empty:
        return {}
    
    
    # Konverter timestamp til datetime og sørger for at alle verdier under 'value' er tall

    result_df['value'] = pd.to_numeric(result_df['value'], errors='coerce')
    result_df['referenceTimestamp'] = pd.to_datetime(result_df['referenceTimestamp'], errors='coerce')
    result_df = result_df.dropna(subset=['referenceTimestamp'])  # Fjern rader med ugyldig tid
        
        
    # Fjern store avvik ved hjelp av Z-score
    result_df['value'] = result_df.groupby('datatype')['value'].transform(
        lambda x: x.where(np.abs(zscore(x)) < 3)
    )
    
    
    # Fyll inn manglende verdier ved hjelp av lineær regresjon
    for datatype in datatyper:
        subset = result_df[result_df['datatype'] == datatype].copy()
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
        
        result_df.update(subset)  
    
    #Legger sammen nedbørsmengde for hver dag og får formatert om til dictionary med dato som key og datatype og måling som value i form av key-value par i en ny dictionary
    result = {}
    grouped = df.groupby(['referenceTimestamp', 'datatype'])
    
    for (timestamp, datatype), group in grouped:
        if timestamp not in result:
            result[timestamp] = {}
        
        total_value = group['value'].sum() if 'precipitation_amount' in datatype else group['value'].values[0]
        result[timestamp][datatype] = {
            'value': total_value,
            'unit': group['unit'].values[0]
        }
    
    return result

    
#print(csv_reader('/Users/kristiansolberg1/Library/CloudStorage/OneDrive-NTNU/Anvendt programmering/Mappeprosjekt/miljodataAnalyse-1/data/met_data.csv', 'sum(precipitation_amount P1D)'))