import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from predictions import predict_from_csv

def show():
    st.title("Fremtidsprediksjon basert på værdata")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    selected_file = st.selectbox("Velg datakilde (CSV)", sorted(data_files))
    file_path = os.path.join(data_dir, selected_file)

    freq = st.selectbox("Frekvens", options=["W", "MS"], index=1)
    periods = st.slider("Antall fremtidige perioder", min_value=3, max_value=36, value=12)
    start_date = st.date_input("Vis historikk fra og med", pd.to_datetime("2022-01-01"))

    try:
        forecast_df, historical_df = predict_from_csv(file_path, freq, periods)
        historical_df = historical_df[historical_df['referenceTimestamp'] >= pd.to_datetime(start_date)]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(historical_df['referenceTimestamp'], historical_df['historical_value'], label='Historiske data')
        ax.plot(forecast_df['timestamp'], forecast_df['predicted_value'], linestyle='--', marker='o', label='Predikert')
        ax.set_title(f'Prediksjon basert på {selected_file}')
        ax.set_xlabel('Tid')
        ax.set_ylabel('Verdi')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        with st.expander("Vis tabeller"):
            st.subheader("Historiske data (filtrert)")
            st.dataframe(historical_df)
            st.subheader("Predikert fremtid")
            st.dataframe(forecast_df)

    except Exception as e:
        st.error(f"Kunne ikke beregne prediksjon: {e}")
