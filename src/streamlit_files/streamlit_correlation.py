import streamlit as st
import pandas as pd
import os
import sys
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.correlation_utils import load_data, calculate_correlation


def show():
    st.title("Sammenligning av værdata")

    # Sett opp datakatalog
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'oslo_2015-2025')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    # Velg to ulike filer
    selected_file1 = st.selectbox("Velg første datakilde", sorted(data_files))
    selected_file2 = st.selectbox("Velg andre datakilde", data_files)

    while selected_file1 == selected_file2:
        st.warning("Kan ikke velge samme fil to ganger. Velg en annen fil.")
        selected_file2 = st.selectbox("Velg andre datakilde (CSV)", sorted(data_files))

    file_path1 = os.path.join(data_dir, selected_file1)
    file_path2 = os.path.join(data_dir, selected_file2)

    df = load_data(file_path1, file_path2)
    if df.empty:
        st.warning("Ingen data ble hentet. Sjekk format og felles datoer i filene.")
        return

    st.write(f"Antall datapunkter totalt: {len(df)}")

    start_date = st.date_input("Startdato", value=pd.to_datetime("2015-01-01"))
    end_date = st.date_input("Sluttdato", value=pd.to_datetime("2025-01-01"), min_value=start_date)

    df_filtered = df[(pd.to_datetime(df['referenceTimestamp']) >= pd.Timestamp(start_date)) &
                     (pd.to_datetime(df['referenceTimestamp']) <= pd.Timestamp(end_date))]

    st.write(f"Antall viste datapunkter: {len(df_filtered)}")

    # Behold kopi av originalene
    df_original = df_filtered.copy()

    # Standardiserte verdier for plotting
    df_filtered['value_1'] = (df_filtered['value_1'] - df_filtered['value_1'].mean()) / df_filtered['value_1'].std()
    df_filtered['value_2'] = (df_filtered['value_2'] - df_filtered['value_2'].mean()) / df_filtered['value_2'].std()


    # Korrelasjon (beregnes på originalene)
    corr = calculate_correlation(df_original)
    if corr is None:
        st.warning("Kunne ikke beregne korrelasjon. Manglende kolonner?")
    else:
        if abs(corr) < 0.3:
            st.warning(f"Svak korrelasjon ({corr:.2f}) liten eller ingen sammenheng.")
        elif abs(corr) > 0.7:
            st.success(f"Kraftig korrelasjon ({corr:.2f}) datasettene følger hverandre godt.")
        else:
            st.info(f"Moderat korrelasjon ({corr:.2f}).")

        retning = "positiv" if corr > 0 else "negativ"
        st.markdown(f"**Retning:** {retning} sammenheng.")

    # Tidsserieplot med standardiserte verdier
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_filtered['referenceTimestamp'], y=df_filtered['value_1'],
                              mode='lines', name='Dataset 1 (standardisert)'))
    fig1.add_trace(go.Scatter(x=df_filtered['referenceTimestamp'], y=df_filtered['value_2'],
                              mode='lines', name='Dataset 2 (standardisert)'))
    fig1.update_layout(title='Tidsserie (standardiserte verdier)',
                       xaxis_title='Tid', yaxis_title='Relativ verdi')
    st.plotly_chart(fig1)

    # Scatterplot med originale verdier
    fig2 = px.scatter(df_original, x='value_1', y='value_2',
                      title='Spredningsplot (originale verdier)',
                      labels={'value_1': 'Dataset 1', 'value_2': 'Dataset 2'})
    st.plotly_chart(fig2)

    # Vis data
    st.subheader("Tabell med standardiserte og originale data")
    df_visning = df_filtered.copy()
    df_visning['original_value_1'] = df_original['value_1']
    df_visning['original_value_2'] = df_original['value_2']
    st.dataframe(df_visning)
