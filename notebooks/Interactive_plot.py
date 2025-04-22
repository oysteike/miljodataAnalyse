import streamlit as st
import os
import sys

src_path = os.path.abspath(os.path.join(os.getcwd(), "src"))
sys.path.append(src_path)

from heatmap_utils import (
    load_data, filter_data, interpolate_data,
    make_map, plot_legend
)

# Sti til datamappe
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'Jan_2025'))
OUTFILE = "weather_map.html"

st.title("🌦️ Nedbør i januar 2025 – Interpolert heatmap")

# 1. Last inn data
_df = load_data(DATA_DIR)

# 2. Velg datatype (f.eks. precipitation, temperature)
available_types = sorted(_df['datatype'].unique())
datatype = st.selectbox("Velg værtype", available_types)

# 3. Finn maksimal verdi for valgt datatype (for skalering)
max_monthly_value = _df[_df['datatype'] == datatype]["value"].max()

# 4. Velg dato (bruk piltaster i Streamlit)
dates = sorted(_df['referenceTimestamp'].unique())
selected_index = st.number_input("Bla gjennom dager", min_value=0, max_value=len(dates)-1, value=0, step=1)
selected_date = dates[selected_index]
st.write(f"📅 Valgt dato: {selected_date}")

# 5. Fastsett heatmap-parametere (kunne også vært brukerjustert)
radius    = 80
intensity = 0.7
threshold = 0.05

# 6. Filtrer og interpoler data
filtered_df = filter_data(_df, datatype, selected_date, max_monthly_value)
interp_df = interpolate_data(filtered_df)

# 7. Lag kart og vis
deck = make_map(interp_df, radius, intensity, threshold)
if deck:
    st.pydeck_chart(deck)

# 8. Fargeskala (legende) vises bare hvis det er data
if not filtered_df.empty:
    min_val = filtered_df["value"].min()
    st.subheader("Fargeskala")
    st.write(f"**Verdier: {min_val:.1f} mm – {max_monthly_value:.1f} mm**")
    legend = plot_legend(min_val, max_monthly_value)
    st.image(legend)

# 9. Ekspander for å vise rådata og statistikk
with st.expander("📊 Rådata og statistikk"):
    st.write("Antall opprinnelige punkter:", len(filtered_df))
    st.dataframe(filtered_df[["lat", "lon", "value"]].head())
    st.write(filtered_df["value"].describe())
    st.write("Antall interpolerte punkter:", len(interp_df))

# 10. Eksport til HTML
if deck and st.button("💾 Eksporter heatmap til HTML"):
    deck.to_html(OUTFILE, open_browser=False)
    st.success(f"Heatmap lagret som {OUTFILE}")
