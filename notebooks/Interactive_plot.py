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
MAPBOX_TOKEN = "pk.eyJ1IjoiZ2Vvcmdicm8iLCJhIjoiY205bXFudjFhMGViMDJqcXV3eW54Y2dqeSJ9.pr7FzSwAzpFvgpFupzOuWg"

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
filtered_df = filtered_df[filtered_df["value"] > 0]
filtered_df["scaled_value"] = filtered_df["value"] * 10  # eller mer


# --- kartstil ---
map_style = f"mapbox://styles/mapbox/light-v9?access_token={MAPBOX_TOKEN}"

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
    initial_view_state=view_state,
    map_style=map_style
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

# HeatmapLayer med justerte parametere
layer = pdk.Layer(
    "HeatmapLayer",
    data=filtered_df,
    get_position=[LON, LAT],
    get_weight="scaled_value",
    radiusPixels=70,       
    intensity=2,           # Standard er 1, men du kan prøve f.eks. 2
    threshold=0.06,        # Gjør kartet mer sensitivt (default 0.03)
    aggregation='MEAN',   # Eller 'SUM', avhenger av hva du ønsker
    opacity=0.9
)

view_state = pdk.ViewState(
    longitude=mid_lon,
    latitude=mid_lat,
    zoom=7,
    pitch=0,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=map_style,  # Bruk riktig map_style med nøkkel
)

# Gir oversikt over datamengde og innhold
st.write("Antall rader i data:", len(filtered_df))
st.dataframe(filtered_df.head())

# Gir oversikt over values
st.write(filtered_df["value"].describe())
st.write("Antall NaN:", filtered_df["value"].isna().sum())



# --- Skriv ut til HTML ---
deck.to_html(
    OUTFILE,
    open_browser=False       # Ikke åpne automatisk
)

print(f"Generert HTML-side: {OUTFILE}")
