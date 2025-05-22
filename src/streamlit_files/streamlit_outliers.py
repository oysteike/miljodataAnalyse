import streamlit as st
import os
import sys
import pandas as pd

def show():
    st.title("Identifisering av uteliggere i værdata")
    st.write("Denne funksjonen lar deg laste opp en CSV-fil med værdata og identifisere eventuelle uteliggere i dataene. Datasettene som er brukt til predektiv analyse og korrelasjon.")

    # Velg datakilde
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'outliers')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    selected_file = st.selectbox("Velg datakilde (CSV)", sorted(data_files))
    file_path = os.path.join(data_dir, selected_file)

    # Last opp fil
    try:
        df = pd.read_csv(file_path)
        st.write(f"Antall datapunkter: {len(df)}")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Kunne ikke laste opp filen: {e}. Vennligst sjekk filformatet og prøv igjen.")
        

