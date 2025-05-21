import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

from sklearn.metrics import r2_score

# Legg til src/ i path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.predictions import predict_from_csv

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
        forecast_df, historical_df, evaluation_df, mse = predict_from_csv(file_path, freq, periods)

        # Filtrer historiske data etter valgt dato
        historical_df = historical_df[historical_df['referenceTimestamp'] >= pd.to_datetime(start_date)]

        # Plot historiske + fremtidige data
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(historical_df['referenceTimestamp'], historical_df['historical_value'], label='Historiske data')
        ax.plot(forecast_df['timestamp'], forecast_df['predicted_value'], linestyle='--', marker='o', label='Predikert')
        ax.set_title(f'Prediksjon basert på {selected_file}')
        ax.set_xlabel('Tid')
        ax.set_ylabel('Verdi')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # Modellens ytelse
        rmse = np.sqrt(mse)
        r2 = r2_score(evaluation_df['actual_value'], evaluation_df['predicted_value'])

        st.subheader("Modellens ytelse på testsett")
        st.markdown(f"""
        - **Mean Squared Error (MSE):** `{mse:.2f}`  
        - **Root Mean Squared Error (RMSE):** `{rmse:.2f}`  
        - **Forklart varians (R²-score):** `{r2:.2f}`
        """)

        # Forklaring på modellens kvalitet
        st.subheader("Vurdering av modellens kvalitet")
        if r2 > 0.8:
            st.success("Modellen forklarer en stor del av variasjonen i dataene. Dette anses som **svært god ytelse**.")
        elif r2 > 0.6:
            st.info("Modellen har **akseptabel ytelse**. Den fanger opp hovedtrendene, men kunne vært forbedret.")
        elif r2 > 0.4:
            st.warning("Modellen har **begrenset forklaringsevne**. Resultatene bør tolkes med forsiktighet.")
        else:
            st.error("Modellen forklarer lite av variasjonen i dataene. Du bør vurdere å forbedre datagrunnlaget eller metoden.")

        # Tabeller
        with st.expander("Vis historiske og predikerte data"):
            st.subheader("Historiske data (filtrert)")
            st.dataframe(historical_df)
            st.subheader("Predikert fremtid")
            st.dataframe(forecast_df)

        with st.expander("Vis testresultater (validering)"):
            st.subheader("Faktiske vs. predikerte verdier fra testsett")
            st.dataframe(evaluation_df)

            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(evaluation_df['referenceTimestamp'], evaluation_df['actual_value'], label='Faktisk')
            ax2.plot(evaluation_df['referenceTimestamp'], evaluation_df['predicted_value'], linestyle='--', label='Predikert')
            ax2.set_title("Validering av modell på testsett")
            ax2.set_xlabel("Tid")
            ax2.set_ylabel("Verdi")
            ax2.grid(True)
            ax2.legend()
            st.pyplot(fig2)

    except Exception as e:
        st.error(f"Kunne ikke beregne prediksjon: {e}")
