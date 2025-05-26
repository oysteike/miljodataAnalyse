import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
from processing.temperature_calculations import analyze_temperature_progress

def show():
    st.title("Temperaturutvikling i lys av Parisavtalen")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data', 'temperature_since_2015')
    target = 1.5  # Parisavtalens mål

    df, progress, reduction_per_year = analyze_temperature_progress(data_dir)

    if progress is not None and not df.empty:
        try:
            st.write("Denne siden forsøker å gi et bilde av hvordan temperaturen i Norge utvikler seg i forhold til målet satt ved Parisavtalen.")

            st.markdown(f"""
            - **År:** {progress['latest_year']}
            - **Temperaturavvik dette året:** {progress['latest_anomaly']:.2f} °C  
            - **Avvik fra mål:** {progress['overshoot']:.2f} °C  
            - **På rett spor:** {'Ja' if progress['on_track'] else 'Nei'}  
            - **Nødvendig reduksjon per år:** {reduction_per_year:.2f} °C
            """)
            if 'referenceTimestamp' in df.columns and 'anomaly' in df.columns:
                st.subheader("Temperaturavvik fra normalverdier (1990-2020)")

                fig_monthly = px.scatter(
                    df,
                    x='referenceTimestamp',
                    y='anomaly',
                    title="Månedlig temperaturavvik",
                    labels={'referenceTimestamp': 'År', 'anomaly': 'Avvik fra normal (°C)'},
                    color_discrete_sequence=['blue'],
                    opacity=0.6
                )
                fig_monthly.add_hline(
                    y=target,
                    line_dash='dash',
                    line_color='red',
                    annotation_text=f"Mål: {target} °C",
                    annotation_position="top left"
                )
                st.plotly_chart(fig_monthly, use_container_width=True)

                df['year'] = df['referenceTimestamp'].dt.year
                annual_df = df.groupby('year')['anomaly'].mean().reset_index()

                fig_annual = px.scatter(
                    annual_df,
                    x='year',
                    y='anomaly',
                    title="Årlig temperaturavvik",
                    labels={'year': 'År', 'anomaly': 'Avvik fra normal (°C)'},
                    color_discrete_sequence=['green'],
                    opacity=0.8
                )
                fig_annual.add_hline(
                    y=target,
                    line_dash='dash',
                    line_color='red',
                    annotation_text=f"Mål: {target} °C",
                    annotation_position="top left"
                )
                st.plotly_chart(fig_annual, use_container_width=True)

            else:
                st.warning("Datasettet mangler nødvendige kolonner for å vise grafer.")
        except Exception as e:
            st.error(f"Feil under plotting av grafer: {e}")
    else:
        st.error("Ingen gyldige data tilgjengelig for analyse.")
