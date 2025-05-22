import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.temperature_calculations import analyze_temperature_progress

def show():
    st.title("Temperaturutvikling i Norge")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'temperature_since_2015')
    target = 1.5  # Parisavtalens mål

    df, progress, reduction_per_year = analyze_temperature_progress(data_dir)

    st.subheader("Oversikt over temperaturendringer")
    st.write(f"År: {progress['latest_year']}")
    st.write(f"Temperaturavvik dette året: {progress['latest_anomaly']:.2f} °C")
    st.write(f"Avvik fra mål: {progress['overshoot']:.2f} °C")
    st.write(f"På rett spor: {'Ja' if progress['on_track'] else 'Nei'}")
    st.write(f"Nødvendig reduksjon per år: {reduction_per_year:.2f} °C")

    st.subheader("Temperaturavvik siden Parisavtalen (baseline: 1990–2020)")
    st.write("Rød linje representerer endringen i temperatur vi ønsker å holde oss under. Mens prikkene viser avviket fra normal temperatur i Norge.")

    # Plotter månedlig gjennomsnittelig temperaturavvik
    fig_monthly = px.scatter(
        df,
        x='referenceTimestamp',
        y='anomaly',
        title="Månedlig temperaturavvik",
        labels={'referenceTimestamp': 'År', 'anomaly': 'Avvik fra normal (°C)'},
        color_discrete_sequence=['blue'],
        opacity=0.6
    )
    fig_monthly.add_hline(y=target, line_dash='dash', line_color='red', annotation_text=f"Mål: {target} °C", annotation_position="top left")
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Plotter årlig gjennomsnittlig temperaturavvik
    df['year'] = df['referenceTimestamp'].dt.year
    annual_df = df.groupby('year')['anomaly'].mean().reset_index()

    fig_annual = px.scatter(
        annual_df,
        x='year',
        y='anomaly',
        title="Årlig temperaturavvik",
        labels={'year': 'År', 'anomaly': 'Avvik fra normal (°C)'},
        color_discrete_sequence=['green'],
        opacity=0.8
    )
    fig_annual.add_hline(y=target, line_dash='dash', line_color='red', annotation_text=f"Mål: {target} °C", annotation_position="top left")
    st.plotly_chart(fig_annual, use_container_width=True)

    st.write("NB! Denne analysen er så forenklet at den ikke er egnet for å trekke konklusjoner om klimaendringer. Justeringer i temperatur må ses i en større sammenheng enn kun målinger fra enkelte måneder i enkelte land. Dette er kun med på å illustrere hvordan en slik analyse kan gjøres.")
