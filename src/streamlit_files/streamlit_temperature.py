import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
from temperature_calculations import analyze_temperature_progress

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

    st.subheader("Temperaturavvik siden Parisavtalen (baseline: 1963–1990)")

    # Månedlig visning
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.scatter(df['referenceTimestamp'], df['anomaly'], color='blue', alpha=0.6, label='Månedlig avvik')
    ax1.axhline(y=target, color='red', linestyle='--', label=f'Mål: {target} °C')
    ax1.set_title("Månedlig temperaturavvik")
    ax1.set_xlabel("År")
    ax1.set_ylabel("Avvik fra normal (°C)")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    # Årlig visning
    df['year'] = df['referenceTimestamp'].dt.year
    annual_df = df.groupby('year')['anomaly'].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.scatter(annual_df['year'], annual_df['anomaly'], color='green', alpha=0.8, label='Årlig snitt')
    ax2.axhline(y=target, color='red', linestyle='--', label=f'Mål: {target} °C')
    ax2.set_title("Årlig temperaturavvik")
    ax2.set_xlabel("År")
    ax2.set_ylabel("Avvik fra normal (°C)")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    st.write("NB! Denne analysen er så forenklet at den ikke er egnet for å trekke konklusjoner om klimaendringer. Justeringer i temperatur må ses i en større sammenheng enn kun målinger fra enkelte måneder i enkelte land. Dette er kun med på å illustrere hvordan en slik analyse kan gjøres.")
