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
    st.title("Fremtidsprediksjon basert på historisk data")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'oslo_2015-2025')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    selected_file = st.selectbox("Velg datakilde (CSV)", sorted(data_files))
    file_path = os.path.join(data_dir, selected_file)

    freq = st.selectbox("Frekvens", options=["W", "MS"], index=1)
    periods = st.slider("Antall fremtidige perioder", min_value=1, max_value=36, value=12)
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

                # --- Ny graf: viser interpolerte datapunkter fra originalfilen ---
        st.subheader("Datapunkter og interpolasjon i originalfilen")

        raw_df = pd.read_csv(file_path, parse_dates=['referenceTimestamp'])
        if 'is_interpolated' in raw_df.columns:
            raw_df = raw_df[raw_df['value'].notna()]
            raw_df = raw_df.sort_values('referenceTimestamp')

            # Legg inn disse to linjene:
            original = raw_df[~raw_df['is_interpolated']]
            interpolated = raw_df[raw_df['is_interpolated']]

            fig3, ax3 = plt.subplots(figsize=(10, 4))


            # Originale verdier: tynnere linje, litt gjennomsiktig
            ax3.plot(original['referenceTimestamp'], original['value'],
                    label="Originale verdier", linewidth=1.2, alpha=0.7, zorder=1)

            # Interpolerte verdier: foran, større og tydeligere
            ax3.scatter(interpolated['referenceTimestamp'], interpolated['value'],
                        color='orange', marker='x', label="Interpolerte verdier",
                        s=60, linewidths=1.5, zorder=2)

            ax3.set_title("Alle verdier i datafilen (med interpolasjon)")
            ax3.set_xlabel("Tid")
            ax3.set_ylabel("Verdi")
            ax3.grid(True)
            ax3.legend()
            st.pyplot(fig3)

        else:
            st.info("Filen inneholder ikke informasjon om interpolerte verdier.")


    except Exception as e:
        st.error(f"Kunne ikke beregne prediksjon: {e}")
