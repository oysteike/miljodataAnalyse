
import streamlit as st
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# 🔁 Legg til src/ i path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.append(src_path)

# 🔁 Importer moduler
from heatmap_utils import (
    load_data, filter_data, interpolate_data,
    make_map, plot_legend
)
from predictions import predict_from_csv

# 🔀 Menyvalg
st.sidebar.title("Navigasjon")
valg = st.sidebar.radio("Velg funksjon:", ["🌦️ Interpolert heatmap", "📈 Fremtidsprediksjon"])

# === 🌦️ HEATMAP DEL ===
if valg == "🌦️ Interpolert heatmap":
    st.title("🌦️ Nedbør i januar 2025 – Interpolert heatmap")

    DATA_DIR = os.path.join(current_dir, 'data', 'Jan_2025')
    OUTFILE = "weather_map.html"

    _df = load_data(DATA_DIR)
    available_types = sorted(_df['datatype'].unique())
    datatype = st.selectbox("Velg værtype", available_types)

    max_monthly_value = _df[_df['datatype'] == datatype]["value"].max()
    dates = sorted(_df['referenceTimestamp'].unique())
    selected_index = st.number_input("Bla gjennom dager", min_value=0, max_value=len(dates)-1, value=0, step=1)
    selected_date = dates[selected_index]
    st.write(f"📅 Valgt dato: {selected_date}")

    radius = 80
    intensity = 0.7
    threshold = 0.05

    filtered_df = filter_data(_df, datatype, selected_date, max_monthly_value)
    interp_df = interpolate_data(filtered_df)
    deck = make_map(interp_df, radius, intensity, threshold)

    if deck:
        st.pydeck_chart(deck)

    if not filtered_df.empty:
        min_val = filtered_df["value"].min()
        st.subheader("Fargeskala")
        st.write(f"**Verdier: {min_val:.1f} mm – {max_monthly_value:.1f} mm**")
        legend = plot_legend(min_val, max_monthly_value)
        st.image(legend)

    with st.expander("📊 Rådata og statistikk"):
        st.write("Antall opprinnelige punkter:", len(filtered_df))
        st.dataframe(filtered_df[["lat", "lon", "value"]].head())
        st.write(filtered_df["value"].describe())
        st.write("Antall interpolerte punkter:", len(interp_df))

    if deck and st.button("💾 Eksporter heatmap til HTML"):
        deck.to_html(OUTFILE, open_browser=False)
        st.success(f"Heatmap lagret som {OUTFILE}")

# === 📈 FREMTIDSPREDIKSJON ===
elif valg == "📈 Fremtidsprediksjon":
    st.title("📈 Fremtidsprediksjon med sesongvariasjon")

    data_files = [f for f in os.listdir(os.path.join(current_dir, "data")) if f.endswith(".csv")]
    selected_file = st.selectbox("Velg datakilde (CSV)", sorted(data_files))
    file_path = os.path.join(current_dir, "data", selected_file)

    freq = st.selectbox("Frekvens", options=["W", "MS"], index=1, help="W = ukentlig, MS = månedlig")
    periods = st.slider("Antall fremtidige perioder", min_value=3, max_value=36, value=12)
    start_date = st.date_input("Vis historikk fra og med", pd.to_datetime("2022-01-01"))

    try:
        forecast_df, historical_df = predict_from_csv(file_path, freq, periods)
        historical_df = historical_df[historical_df['referenceTimestamp'] >= pd.to_datetime(start_date)]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(historical_df['referenceTimestamp'], historical_df['historical_value'], label='Historiske data')
        ax.plot(forecast_df['timestamp'], forecast_df['predicted_value'], linestyle='--', marker='o', label='Predikert')

        ax.set_title(f'Prediksjon basert på "{selected_file}"')
        ax.set_xlabel('Tid')
        ax.set_ylabel('Verdi')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        with st.expander("📊 Vis tabeller"):
            st.subheader("Historiske data (filtrert)")
            st.dataframe(historical_df)
            st.subheader("Predikert fremtid")
            st.dataframe(forecast_df)

    except Exception as e:
        st.error(f"Kunne ikke beregne prediksjon: {e}")
