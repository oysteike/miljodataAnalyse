import streamlit as st
import pandas as pd
import glob
import os
import pydeck as pdk
import datetime
import numpy as np
from scipy.interpolate import griddata

# ----------------------------------------------------------------------------
# Streamlit-app: Heatmap for værdata i januar 2025 over hele landet
# ----------------------------------------------------------------------------

# --- KONFIGURASJON ---
DATA_DIR    = os.getcwd()  # Rotmappe for data/data/Jan_2025/*.csv
TIMESTAMP   = "referenceTimestamp"
LON         = "lon"
LAT         = "lat"
VALUE       = "value"
OUTFILE     = 'weather_map.html'
MAPBOX_TOKEN = (
    "pk.eyJ1IjoiZ2Vvcmdicm8iLCJhIjoiY205bXFudjFhMGViMDJqcXV3eW54Y2dqeSJ9."
    "pr7FzSwAzpFvgpFupzOuWg"
)
MAP_STYLE = f"mapbox://styles/mapbox/light-v9?access_token={MAPBOX_TOKEN}"

# ----------------------------------------------------------------------------
# FUNKSJONER
# ----------------------------------------------------------------------------

def load_data(data_dir):
    """
    Leser inn alle CSV-filer for januar 2025 og tagger dem med datatype hentet fra filnavn.
    Returnerer en sammenslått DataFrame.
    """
    dfs = []
    for path in glob.glob(os.path.join(data_dir, "data", "Jan_2025", "*.csv")):
        fname = os.path.splitext(os.path.basename(path))[0]
        mtype = fname.split("_")[0]

        df = pd.read_csv(path)
        df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP], utc=True)
        df["referenceTimestamp"] = df[TIMESTAMP].dt.date.astype(str)
        df["datatype"] = mtype
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def filter_data(df, datatype, selected_date):
    """
    Filtrerer etter ønsket datatype og dato. Beholder også nullverdier.
    """
    df2 = df[
        (df['datatype'] == datatype) &
        (df['referenceTimestamp'] == selected_date)
    ].copy()

    # Skaler verdier for heatmap – viktig å ta med nuller!
    df2['scaled_value'] = df2[VALUE] * 10
    return df2

def interpolate_data(df, grid_res=200):
    """
    Interpolerer måledata over et grid ved hjelp av scipy.griddata.
    Fjerner NaN før interpolasjon. Returnerer interpolert DataFrame.
    """
    # Fjern rader med NaN i nødvendige kolonner før interpolasjon
    df_clean = df.dropna(subset=[LON, LAT, 'scaled_value'])

    if len(df_clean) < 3:
        return df_clean  # For få punkter til interpolasjon

    grid_lon = np.linspace(df_clean[LON].min(), df_clean[LON].max(), grid_res)
    grid_lat = np.linspace(df_clean[LAT].min(), df_clean[LAT].max(), grid_res)
    grid_x, grid_y = np.meshgrid(grid_lon, grid_lat)

    points = df_clean[[LON, LAT]].values
    values = df_clean['scaled_value'].values
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    interp_df = pd.DataFrame({
        LON: grid_x.flatten(),
        LAT: grid_y.flatten(),
        'scaled_value': grid_z.flatten()
    }).dropna()

    return interp_df

def make_map(df, radius, intensity, threshold):
    """
    Genererer et pydeck heatmap for gitt DataFrame og parametere.
    """
    if df.empty:
        st.warning("Ingen data tilgjengelig for valgt kombinasjon.")
        return None

    view_state = pdk.ViewState(
        latitude=df[LAT].mean(),
        longitude=df[LON].mean(),
        zoom=6,
        pitch=0
    )

    layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=[LON, LAT],
        get_weight="scaled_value",
        radiusPixels=radius,
        intensity=intensity,
        threshold=threshold,
        aggregation='MEAN',
        opacity=0.8
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=MAP_STYLE
    )

# ----------------------------------------------------------------------------
# HOVEDPROGRAM
# ----------------------------------------------------------------------------

st.title("🌦️ Været i januar 2025 – Interpolert heatmap over hele landet")

# 1) Last inn data
_df = load_data(DATA_DIR)

# 2) Velg datatype
available_types = sorted(_df['datatype'].unique())
datatype = st.selectbox("Velg værtype", available_types)

# 3) Bla mellom dager med piltaster
dates = sorted(_df['referenceTimestamp'].unique())
selected_index = st.number_input("Bla gjennom dager", min_value=0, max_value=len(dates)-1, value=0, step=1)
selected_date = dates[selected_index]
st.write(f"📅 Valgt dato: {selected_date}")

# 4) Justerbare heatmap-innstillinger
st.sidebar.header("🔧 Heatmap-innstillinger")
radius    = st.sidebar.slider("Radius (pixels)",  10, 200, 70)
intensity = st.sidebar.slider("Intensity",        0.1, 5.0, 0.5)
threshold = st.sidebar.slider("Threshold",        0.0, 1.0, 0.05)

# 5) Filtrer og interpoler data
filtered_df = filter_data(_df, datatype, selected_date)
interp_df = interpolate_data(filtered_df)

# 6) Generer og vis kart
deck = make_map(interp_df, radius, intensity, threshold)
if deck:
    st.pydeck_chart(deck)

# 7) Detaljer og eksport
with st.expander("📊 Vis rådata og statistikk"):
    st.write("Antall opprinnelige datapunkter:", len(filtered_df))
    st.dataframe(filtered_df[[LAT, LON, VALUE]].head())
    st.write(filtered_df[VALUE].describe())
    st.write("Antall interpolerte punkter:", len(interp_df))

if deck and st.button("💾 Eksporter heatmap til HTML"):
    deck.to_html(OUTFILE, open_browser=False)
    st.success(f"Heatmap lagret som {OUTFILE}")
