import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path1, file_path2):
    """
    Leser inn to CSV-filer og sammenligner dem basert på kolonnene 'referenceTimestamp' og 'value'.
    Returnerer en DataFrame med forskjeller mellom de to datasettene.
    """
    #try:
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)

    df1['referenceTimestamp'] = pd.to_datetime(df1['referenceTimestamp'])
    df2['referenceTimestamp'] = pd.to_datetime(df2['referenceTimestamp'])
    df1['value'] = pd.to_numeric(df1['value'])
    df2['value'] = pd.to_numeric(df2['value'])

    # Slå sammen dataene basert på 'referenceTimestamp'
    merged_df = pd.merge(df1, df2, on='referenceTimestamp', suffixes=('_1', '_2'))

    # Beregn forskjellen mellom de to datasettene
    merged_df['difference'] = merged_df['value_1'] - merged_df['value_2']

    return merged_df[['referenceTimestamp', 'value_1', 'value_2', 'difference']]

    #except Exception as e:
    #   return pd.DataFrame()

def plot_weather_dashboard(df):
    """
    Visualiserer to kolonner ('value_1' og 'value_2') fra en DataFrame returnert av load_data.
    Lager tidsserieplot, korrelasjonsanalyse og scatterplot.
    Returnerer figurene og korrelasjonskoeffisienten.
    """
    if df.empty or not {'referenceTimestamp', 'value_1', 'value_2', 'difference'}.issubset(df.columns):
        return None, None, None

    # Tidsserieplot
    fig1, ax1 = plt.subplots()
    ax1.plot(df['referenceTimestamp'], df['value_1'], label='value_1')
    ax1.plot(df['referenceTimestamp'], df['value_2'], label='value_2')
    ax1.set_xlabel('Tid')
    ax1.set_ylabel('Verdi')
    ax1.legend()

    # Forskjell over tid
    fig2, ax2 = plt.subplots()
    ax2.plot(df['referenceTimestamp'], df['difference'], label='Forskjell (value_1 - value_2)', color='purple')
    ax2.set_xlabel('Tid')
    ax2.set_ylabel('Forskjell')
    ax2.legend()

    # Scatterplot
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=df['value_1'], y=df['value_2'], ax=ax3)
    ax3.set_xlabel('value_1')
    ax3.set_ylabel('value_2')

    return fig1, fig2, fig3

def calculate_correlation(df, var1='value_1', var2='value_2'):
    """
    Beregner korrelasjonen mellom to variabler og gir en vurdering av styrke, retning og logisk sammenheng.
    """
    if df.empty or var1 not in df.columns or var2 not in df.columns:
        return "Data mangler eller kolonner finnes ikke."

    corr = df[var1].corr(df[var2])

    if abs(corr) < 0.3:
        strength = "svak"
    elif abs(corr) < 0.7:
        strength = "moderat"
    else:
        strength = "sterk"

    direction = "positiv" if corr > 0 else "negativ"
    comment = f"Korrelasjonen mellom {var1} og {var2} er {direction} og {strength} (r = {corr:.2f})."

    logical = "Dette er en logisk sammenheng." if strength != "svak" else "Sammenhengen er svak og kan være tilfeldig."
    return comment + " " + logical
