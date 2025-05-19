import streamlit as st
import pandas as pd
import sys, os
import matplotlib.pyplot as plt

sys.path.append('../src')
from predictions import predict_from_csv

# Velger hvilken datafil som skal brukes
data_files = [f for f in os.listdir('../data') if f.endswith('.csv')]
selected_file = st.selectbox('Select a data file:', data_files)
file_path = os.path.join('../data', selected_file)

# Velg frekvens og antall perioder for fremtidsprognosen
freq = st.selectbox('Select frequency:', ['MS', 'W'])
periods = st.number_input('Number of periods to predict:', min_value=1, max_value=100, value=12)

# Velg startdato for fremtidsprognosen
start_date = st.date_input('Select start date:', pd.to_datetime('2023-01-01'))

# Hent data og lag prognose
forecast_df, historical_df = predict_from_csv(file_path, freq, periods)
historical_df = historical_df[historical_df['referenceTimestamp'] >= pd.to_datetime(start_date)]

# Plot med matplotlib og vis i Streamlit
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(historical_df['referenceTimestamp'], historical_df['historical_value'], label='Historiske data')
ax.plot(forecast_df['timestamp'], forecast_df['predicted_value'],
        linestyle='--', marker='o', label='Predikert')

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