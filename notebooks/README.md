# README for Notebooks

Denne mappen inneholder notebooks og interaktive verktøy for å visualisere værdata som nedbør, solskinn og trykk. Du kan også generere HTML-heatmaps for videre bruk.

## Innhold

### 1. `plot_prediction.ipynb`
- **Beskrivelse**: Notebook for å lage prediksjoner basert på historiske værdata.
- **Funksjonalitet**:
  - Leser værdata fra en CSV-fil.
  - Utfører prediksjoner for fremtidige tidsperioder.
  - Visualiserer historiske data og prediksjoner i en graf.
- **Bruk**:
  - Endre `file_path` for å velge datasett (f.eks. nedbør, solskinn eller trykk).
  - Juster parametere som `freq` (frekvens) og `periods` (antall fremtidige perioder).
  - Kjør cellene for å generere grafen.

### 2. `Interactive_plot.py`
- **Beskrivelse**: Interaktiv Streamlit-applikasjon for å lage og visualisere heatmaps.
- **Funksjonalitet**:
  - Leser værdata fra CSV-filer i `data/Jan_2025/`.
  - Lar brukeren velge datatype (f.eks. nedbør, solskinn eller trykk) og dato.
  - Genererer et interpolert heatmap basert på valgte data.
  - Viser en fargeskala (legende) og statistikk for dataene.
  - Eksporterer heatmap som en HTML-fil.
- **Bruk**:
  1. Start applikasjonen med:
     ```bash
     streamlit run Interactive_plot.py
     ```
  2. Velg datatype og dato fra menyen.
  3. Juster parametere som radius og intensitet om nødvendig.
  4. Klikk på "💾 Eksporter heatmap til HTML" for å lagre kartet.

## Krav
- Python 3.9 eller nyere.
- Følgende biblioteker må være installert:
  - `pandas`
  - `matplotlib`
  - `streamlit`
  - `pydeck`
  - `scipy`

## Eksempel på bruk
1. **Prediksjoner**:
   - Åpne `plot_prediction.ipynb` i Jupyter Notebook eller en annen kompatibel editor.
   - Endre filsti og parametere for å tilpasse analysen.
   - Kjør cellene for å generere grafen.

2. **Heatmap**:
   - Start Streamlit-applikasjonen med kommandoen over.
   - Velg ønsket datatype og dato.
   - Visualiser dataene som et heatmap og eksporter til HTML.

## Eksport
- Heatmaps genereres som interaktive HTML-filer som kan åpnes i en nettleser.
- Filene lagres i prosjektmappen med navnet `weather_map.html`.

For mer informasjon, se kommentarene i koden.