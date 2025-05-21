import os
import glob
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
import matplotlib as mpl
from io import BytesIO
import pydeck as pdk

"""
Denne metodne leser inn data fra CSV-filer, filtrerer og interpolerer dem,
og lager et heatmap ved hjelp av pydeck.
Den bruker også matplotlib for å lage en legende for nedbørverdier.
"""

# Konstantnavn for kolonner brukt i datasettet
TIMESTAMP   = "referenceTimestamp"
LON         = "lon"
LAT         = "lat"
VALUE       = "value"

# Mapbox-stil og token (brukes for bakgrunnskart)
MAPBOX_TOKEN = (
    "pk.eyJ1IjoiZ2Vvcmdicm8iLCJhIjoiY205bXFudjFhMGViMDJqcXV3eW54Y2dqeSJ9."
    "pr7FzSwAzpFvgpFupzOuWg"
)
MAP_STYLE = f"mapbox://styles/mapbox/light-v9?access_token={MAPBOX_TOKEN}"

def load_data(data_dir):
    """
    Leser alle CSV-filer i mappen 'data/Jan_2025/' og kombinerer dem til én DataFrame.
    Hver fil antas å ha format: <datatype>_dato.csv
    """
    dfs = []
    for path in glob.glob(os.path.join(data_dir, "*.csv")):
        print(path)
        fname = os.path.splitext(os.path.basename(path))[0]
        mtype = fname.split("_")[0]

        df = pd.read_csv(path)
        df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP], utc=True)
        df["referenceTimestamp"] = df[TIMESTAMP].dt.date.astype(str)
        df["datatype"] = mtype
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def filter_data(df, datatype, selected_date, max_value):
    """
    Filtrerer data etter ønsket datatype og dato.
    """
    df2 = df[
        (df['datatype'] == datatype) &
        (df['referenceTimestamp'] == selected_date)
    ].copy()

    df2['plot_value'] = df2[VALUE]

    return df2

def interpolate_data(df, cutoff_km):
    """
    Interpolerer måledata over et rutenett (grid), men ekskluderer områder
    som ligger for langt unna et faktisk datapunkt.
    """
    grid_res=200
    df_clean = df.dropna(subset=[LON, LAT, 'plot_value'])

    if len(df_clean) < 3:
        return df_clean  # Ikke nok data til interpolasjon

    # Lag et jevnt grid over området
    grid_lon = np.linspace(df_clean[LON].min(), df_clean[LON].max(), grid_res)
    grid_lat = np.linspace(df_clean[LAT].min(), df_clean[LAT].max(), grid_res)
    grid_x, grid_y = np.meshgrid(grid_lon, grid_lat)
    grid_points = np.c_[grid_x.flatten(), grid_y.flatten()]

    # Punktverdier fra rådata
    points = df_clean[[LON, LAT]].values
    values = df_clean['plot_value'].values

    # Interpoler verdier til grid-punktene
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    # Avstand fra hvert gridpunkt til nærmeste datapunkt
    tree = cKDTree(points)
    dist, _ = tree.query(grid_points, k=1)

    # Sett verdier utenfor cutoff til NaN
    grid_z_flat = grid_z.flatten()
    dist_km = dist * 111
    grid_z_flat[dist_km > cutoff_km] = np.nan


    # Returner som DataFrame
    interp_df = pd.DataFrame({
        LON: grid_points[:, 0],
        LAT: grid_points[:, 1],
        'plot_value': grid_z_flat
    }).dropna()

    return interp_df

def make_map(df, radius, intensity, threshold):
    """
    Lager et pydeck heatmap basert på input-data.
    """
    if df.empty:
        return None  # Ikke vis noe hvis det ikke er data

    view_state = pdk.ViewState(
        latitude=df[LAT].mean(),
        longitude=df[LON].mean(),
        zoom=6,
        pitch=0
    )

    # Pydeck heatmap-lag
    layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=[LON, LAT],
        get_weight="plot_value",
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

def plot_legend(min_val, max_val, datatype="nedbør"):
    """
    Lager en fargeskala/legende for nedbør- eller vindverdier.
    Returnerer som bilde i minnet (BytesIO).
    """
    from matplotlib.colors import LinearSegmentedColormap

    if datatype.lower() == "vind":
        colors = ["white", "lightblue", "blue", "navy"]  # Vind: blåskala
        label = "Vind (m/s)"
    else:
        colors = ["white", "yellow", "red"]  # Nedbør: gul-rød
        label = "Nedbør (mm)"

    cmap = LinearSegmentedColormap.from_list("custom_heat", colors)

    fig, ax = plt.subplots(figsize=(6, 0.5))
    fig.subplots_adjust(bottom=0.5)

    norm = mpl.colors.Normalize(vmin=min_val, vmax=max_val)
    cb = mpl.colorbar.ColorbarBase(
        ax, cmap=cmap,
        norm=norm,
        orientation='horizontal'
    )
    cb.set_label(label)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf

def get_colormap(datatype):
    from matplotlib.colors import LinearSegmentedColormap
    if datatype.lower() == "temperatur":
        # Gul -> rød ved 10 grader
        colors = [(0.0, "yellow"), (10/30, "red"), (1.0, "darkred")]
        return LinearSegmentedColormap.from_list("temp", [c[1] for c in colors])
    else:
        # Lys blå -> rød ved 10 mm nedbør
        colors = [(0.0, "lightblue"), (10/30, "red"), (1.0, "darkred")]
        return LinearSegmentedColormap.from_list("rain", [c[1] for c in colors])


def plot_colorbar_for_map(min_val, max_val, datatype="nedbør"):
    """
    Lager og viser en colorbar for bruk sammen med pydeck heatmap.
    """
    cmap = get_colormap(datatype)
    fig, ax = plt.subplots(figsize=(6, 0.5))
    fig.subplots_adjust(bottom=0.5)
    norm = mpl.colors.Normalize(vmin=min_val, vmax=max_val)
    cb = mpl.colorbar.ColorbarBase(
        ax, cmap=cmap,
        norm=norm,
        orientation='horizontal'
    )
    cb.set_label("Vind (m/s)" if datatype.lower() == "vind" else "Nedbør (mm)")
    plt.show()
