import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def load_data(file_path1, file_path2):
    """
    Leser inn to CSV-filer og sammenligner dem basert på kolonnene 'referenceTimestamp' og 'value'.
    Returnerer en DataFrame med forskjeller mellom de to datasettene.
    """
    try:
        df1 = pd.read_csv(file_path1)
        df2 = pd.read_csv(file_path2)

        df1['referenceTimestamp'] = pd.to_datetime(df1['referenceTimestamp']).dt.date
        df2['referenceTimestamp'] = pd.to_datetime(df2['referenceTimestamp']).dt.date
        df1['value'] = pd.to_numeric(df1['value'])
        df2['value'] = pd.to_numeric(df2['value'])

        merged_df = pd.merge(df1, df2, on='referenceTimestamp', suffixes=('_1', '_2'))

        if merged_df.empty:
            return pd.DataFrame()
        return merged_df[['referenceTimestamp', 'value_1', 'value_2']]

    except Exception:
        return pd.DataFrame()


def plot_weather_dashboard(df):
    """
    Visualiserer to kolonner ('value_1' og 'value_2') fra en DataFrame returnert av load_data.
    Lager tidsserieplot, korrelasjonsanalyse og scatterplot med Plotly.
    Returnerer figurene og korrelasjonskoeffisienten.
    """
    if df.empty or not {'referenceTimestamp', 'value_1', 'value_2'}.issubset(df.columns):
        return None, None

    # Tidsserieplot
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['referenceTimestamp'], y=df['value_1'], mode='lines', name='value_1'))
    fig1.add_trace(go.Scatter(x=df['referenceTimestamp'], y=df['value_2'], mode='lines', name='value_2'))
    fig1.update_layout(title='Tidsserie', xaxis_title='Tid', yaxis_title='Verdi')

    # Scatterplot
    fig2 = px.scatter(df, x='value_1', y='value_2', title='Sammenheng mellom første og andre element')
    fig2.update_layout(xaxis_title='value_1', yaxis_title='value_2')

    return fig1, fig2


def calculate_correlation(df, var1='value_1', var2='value_2'):
    """
    Beregner korrelasjonen mellom to variabler og gir en vurdering av styrke, retning og logisk sammenheng.
    """
    if df.empty or var1 not in df.columns or var2 not in df.columns:
        return None

    corr = df[var1].corr(df[var2])

    return corr
