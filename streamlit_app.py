import streamlit as st
import os
import sys

# Legg til src i path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.append(src_path)

# Importer visningsmoduler
from streamlit_files.streamlit_heatmap import show as show_heatmap
from streamlit_files.streamlit_prediction import show as show_prediction
from streamlit_files.streamlit_temperature import show as show_temperature
from streamlit_files.streamlit_correlation import show as show_correlation

# Meny
st.sidebar.title("Navigasjon")
valg = st.sidebar.radio("Velg funksjon:", ["Hjem", "Interpolert heatmap", "Fremtidsprediksjon", "Temperaturendringer", "Sammenligning av værdata"])

# Hjem
if valg == "Hjem":
    st.title("Værdata og prediksjoner")
    st.write("Velg en funksjon fra menyen til venstre for å begynne.")
    st.markdown("""
    ### Hva viser denne appen?

    Her får du innsikt i værdata fra hele Norge:

    - **Visualiseringer**: Heatmap og trendgrafer
    - **Prediksjoner**: Fremtidig utvikling i værdata
    - **Interaktive valg**: Velg værtype, dato og mer
    """)
elif valg == "Interpolert heatmap":
    show_heatmap()
elif valg == "Fremtidsprediksjon":
    show_prediction()
elif valg == "Temperaturendringer":
    show_temperature()
elif valg == "Sammenligning av værdata":
    show_correlation()
