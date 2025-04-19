import streamlit as st
import pandas as pd
import glob
import os
import pydeck as pdk

# --- Konfigurasjon ---
DATA_DIR = os.getcwd() # mappe med rain.csv, pressure.csv, osv.
TIMESTAMP = "referenceTimestamp"
LON = "lon"
LAT = "lat"
VALUE = "value"
UNIT = "unit"
OUTFILE = 'weather_map.html'
MAPBOX_TOKEN= os.getenv("pk.eyJ1IjoiZ2Vvcmdicm8iLCJhIjoiY205bXFudjFhMGViMDJqcXV3eW54Y2dqeSJ9.pr7FzSwAzpFvgpFupzOuWg") 

# --- Last alle data inn, slå sammen til én DF ---
def load_all_data(data_dir):
    dfs = []
    for path in glob.glob(os.path.join(data_dir,"data", "Jan_2025", "*.csv")):
        mtype = os.path.splitext(os.path.basename(path))[0]
        df = pd.read_csv(path)
        df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP], utc=True)
        df["referenceTimestamp"] = df[TIMESTAMP].dt.date.astype(str) # som tekst
        df["datatype"] = mtype
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

df = load_all_data(DATA_DIR)

# --- Streamlit-app ---
st.title("Været i januar 2025")

# --- Velg datatype ---
datatypes = df["datatype"].unique()
datatype = st.selectbox("Velg datatype", datatypes)

# --- Velg dager ---
dates = df["referenceTimestamp"].unique()
date = st.slider("Velg dager", min_value=0, max_value=len(dates)-1, value=0)
selected_date = dates[date]

# --- Filtrer data ---
filtered_df = df[(df["datatype"] == datatype) & (df["referenceTimestamp"] == selected_date)]

# --- Lag heatmap ---
view_state = pdk.ViewState(
    latitude=filtered_df[LAT].mean(),
    longitude=filtered_df[LON].mean(),
    zoom=6,
    pitch=0,
    bearing=0
)

layer = pdk.Layer(
    "HeatmapLayer",
    filtered_df,
    pickable=True,
    opacity=0.8,
    radius_scale=100,
    radius_min_pixels=10,
    radius_max_pixels=100,
    get_lat=LAT,
    get_lng=LON,
    get_weight=VALUE
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state
)

st.pydeck_chart(r)

# --- Velg målingstype og dato hardkodet her (kan gjøres dynamisk hvis ønsket) ---
selected_type = "max(surface_air_pressure P1D)"           # eller "pressure", "temp" osv.
selected_date = "2025-01-15"     # ISO-format

df_sel = df[
    (df["datatype"] == selected_type) &
    (df["referenceTimestamp"] == selected_date)
]

# --- Opprett heatmap-laget ---
mid_lon = df_sel[LON].mean()
mid_lat = df_sel[LAT].mean()

layer = pdk.Layer(
    "HeatmapLayer",
    data=df_sel,
    get_position=[LON, LAT],
    get_weight=VALUE,
    radiusPixels=60,
    opacity=0.7,
)

view_state = pdk.ViewState(
    longitude=mid_lon,
    latitude=mid_lat,
    zoom=8,
    pitch=0,
)

# Hvis du bruker Mapbox, må du ha map_style med din Mapbox-nøkkel
if MAPBOX_TOKEN:
    map_style = f"mapbox://styles/mapbox/light-v9?access_token={MAPBOX_TOKEN}"
else:
    map_style = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"  # Bruk OpenStreetMap hvis ingen Mapbox-nøkkel er tilgjengelig

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=map_style,  # Bruk riktig map_style med nøkkel
)

# --- Skriv ut til HTML ---
deck.to_html(
    OUTFILE,
    notebook_display=False,   # Ikke forsøke jupyter‐display
    open_browser=True       # Ikke åpne automatisk
)

print(f"Generert HTML-side: {OUTFILE}")
