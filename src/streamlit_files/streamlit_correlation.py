import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.correlation_utils import load_data, plot_weather_dashboard, calculate_correlation

def show():
    st.title("Sammenligning av værdata")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'oslo_2015-2025')
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    selected_file1 = st.selectbox("Velg første datakilde", sorted(data_files))
    selected_file2 = st.selectbox("Velg andre datakilde", data_files)

    # Sørger for at de to valgene ikke er det samme
    while selected_file1 == selected_file2:
        st.warning("Kan ikke velge samme fil to ganger. Velg en annen fil for andre datakilde.")
        selected_file2 = st.selectbox("Velg andre datakilde (CSV)", sorted(data_files))

    file_path1 = os.path.join(data_dir, selected_file1)
    file_path2 = os.path.join(data_dir, selected_file2)
    st.write(f"Valgte filstier: {file_path1} og {file_path2}")

    df = load_data(file_path1, file_path2)
    st.write(f"Antall datapunkter: {len(df)}")
    st.write(df.head())
    correlation = calculate_correlation(df)
    st.write(f"Korrelasjonskoeffisient mellom {selected_file1} og {selected_file2}: {correlation}")
    fig1, fig2, fig3 = plot_weather_dashboard(df)
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
