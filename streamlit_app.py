
import streamlit as st
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import inspect

# 🔁 Legg til src/ i path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.append(src_path)

# 🔁 Importer moduler
from heatmap_utils import load_data, filter_data, interpolate_data, make_map, plot_legend
from predictions import predict_from_csv
from temperature_calculations import analyze_temperature_progress

# 🔀 Menyvalg
st.sidebar.title("Navigasjon")
valg = st.sidebar.radio("Velg funksjon:", ["Hjem", "🌦️ Interpolert heatmap", "📈 Fremtidsprediksjon", "🌡️ Temperaturendringer"])

# === HOMEPAGE ===
if valg == "Hjem":
    st.title("🌦️ Værdata og prediksjoner")
    st.write("Velg en funksjon fra menyen til venstre for å begynne.")
    st.markdown("""
    ### Hva viser denne appen?

    I denne applikasjonen kan du utforske datasettet og se ulike innsikter, blant annet:

    - **Visualiseringer**: Heatmap, linjediagram og skatterplot for å se trender og mønstre i værdata i Norge.
    - **Prediksjoner**: Forutsi fremtidige værforhold basert på historiske data.
    - **Filtrering**: Mulighet for å filtrere data på tvers av ulike kategorier.
    - **Interaktive komponenter**: Velg hvilke variabler du vil analysere, og se resultatene oppdatere seg dynamisk.
    - **Oversikt over nøkkeltall**: Gjennomsnitt, median, standardavvik m.m.

    Denne appliikasjonen har som mål å gi deg et godt grunnlag for å forstå strukturen i værdataene og identifisere mønstre eller avvik. 
    """)

# === 🌦️ HEATMAP DEL ===
elif valg == "🌦️ Interpolert heatmap":
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


# === 🌡️ TEMPERATURBEREGNINGER ===
elif valg == "🌡️ Temperaturendringer":
    st.title("🌡️ Temperaturendringer")
    DATA_DIR = os.path.join(current_dir, "data", "temperature_since_2015")

    target = 1.5  # Parisavtalens mål for global oppvarming innen 2030
    
    df, progress, reduction_per_year = analyze_temperature_progress(DATA_DIR)
    st.subheader("Analyser temperaturutvikling")
    st.write("Her kan du se hvordan temperaturen har utviklet seg i Norge de siste årene. En modell med ønske om å vekke oppmerksomhet rundt temperaturutviklingen i Norge og hvordan den kan sammenlignes med Parisavtalens mål om 1.5°C global oppvarming innen 2030. Her sammenlignes altså temperaturen i Norge med det snittet vi hadde i perioden 1990-2000.")
    st.write(f"År: {progress['latest_year']}")
    st.write(f"Temperaturavvik dette året: {progress['latest_anomaly']:.2f}°C")
    st.write(f"Avvik fra mål: {progress['overshoot']:.2f}°C")
    st.write(f"Er på rett spor? {'Ja' if progress['on_track'] else 'Nei'}")
    st.write(f"Nødvendig reduksjon per år for å nå målet: {reduction_per_year:.2f}°C")

    st.subheader("Temperaturavvik fra normal siden parisavtalen, i henhold til normale verdier fra 1963-1990")


    # === 1. Plot med månedlige verdier ===
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.scatter(df['referenceTimestamp'], df['anomaly'], color='blue', alpha=0.6, label='Snittemperatur (månedlig)')
    ax1.axhline(y=target, color='red', linestyle='--', label=f'Mål: {target}°C')
    ax1.set_title("Månedlig temperaturavvik i Norge (alle stasjoner kombinert)")
    ax1.set_xlabel("År")
    ax1.set_ylabel("Avvik fra normal (°C)")
    ax1.legend()
    ax1.grid(True)

    st.pyplot(fig1)

    # === 2. Plot med årlige gjennomsnitt ===
    # Beregn årlig gjennomsnitt først
    df['year'] = df['referenceTimestamp'].dt.year
    annual_df = df.groupby('year')['anomaly'].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.scatter(annual_df['year'], annual_df['anomaly'], color='green', alpha=0.8, label='Snittemperatur (årlig)')
    ax2.axhline(y=target, color='red', linestyle='--', label=f'Mål: {target}°C')
    ax2.set_title("Årlig temperaturavvik i Norge")
    ax2.set_xlabel("År")
    ax2.set_ylabel("Avvik fra normal (°C)")
    ax2.legend()
    ax2.grid(True)

    st.pyplot(fig2)

    st.write("NB! Denne analysen er så forenklet at den ikke er egnet for å trekke konklusjoner om klimaendringer. Justeringer i temperatur må ses i en større sammenheng enn kun målinger fra enkelte måneder i enkelte land. Dette er kun med på å illustrere hvordan en slik analyse kan gjøres.")
    