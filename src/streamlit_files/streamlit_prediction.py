import streamlit as st
import os
import pandas as pd
import numpy as np
import sys
import plotly.express as px
import plotly.graph_objects as go
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

        # Historiske og predikerte verdier
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historical_df['referenceTimestamp'], y=historical_df['historical_value'],
                                 mode='lines', name='Historiske data'))
        fig.add_trace(go.Scatter(x=forecast_df['timestamp'], y=forecast_df['predicted_value'],
                                 mode='lines+markers', name='Predikert', line=dict(dash='dash')))
        fig.update_layout(title=f"Prediksjon basert på {selected_file}",
                          xaxis_title="Tid", yaxis_title="Verdi", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # Modellens ytelse
        rmse = np.sqrt(mse)
        r2 = r2_score(evaluation_df['actual_value'], evaluation_df['predicted_value'])

        st.subheader("Modellens ytelse på testsett")
        st.markdown(f"""
        - **Mean Squared Error (MSE):** `{mse:.2f}`  
        - **Root Mean Squared Error (RMSE):** `{rmse:.2f}`  
        - **Forklart varians (R²-score):** `{r2:.2f}`
        """)

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

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=evaluation_df['referenceTimestamp'], y=evaluation_df['actual_value'],
                                      mode='lines', name='Faktisk'))
            fig2.add_trace(go.Scatter(x=evaluation_df['referenceTimestamp'], y=evaluation_df['predicted_value'],
                                      mode='lines', name='Predikert', line=dict(dash='dash')))
            fig2.update_layout(title="Validering av modell på testsett",
                               xaxis_title="Tid", yaxis_title="Verdi", template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

        # Interpolerte verdier
        st.subheader("Datapunkter og interpolasjon i originalfilen")

        raw_df = pd.read_csv(file_path, parse_dates=['referenceTimestamp'])
        if 'is_interpolated' in raw_df.columns:
            raw_df = raw_df[raw_df['value'].notna()]
            raw_df = raw_df.sort_values('referenceTimestamp')

            original = raw_df[~raw_df['is_interpolated']]
            interpolated = raw_df[raw_df['is_interpolated']]

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=original['referenceTimestamp'], y=original['value'],
                                      mode='lines', name="Originale verdier", line=dict(width=1.2), opacity=0.7))
            fig3.add_trace(go.Scatter(x=interpolated['referenceTimestamp'], y=interpolated['value'],
                                      mode='markers', name="Interpolerte verdier", marker=dict(color='orange', symbol='x', size=8)))
            fig3.update_layout(title="Alle verdier i datafilen (med interpolasjon)",
                               xaxis_title="Tid", yaxis_title="Verdi", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Filen inneholder ikke informasjon om interpolerte verdier.")

    except Exception as e:
        st.error(f"Kunne ikke beregne prediksjon: {e}")

