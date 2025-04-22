# Testdokumentasjon

Denne mappen inneholder tester for prosjektet `miljodataAnalyse`, skrevet med `unittest`.

## Testfiler

### `test_connect_API.py`
Tester `FrostDataFetcher`-klassen for å hente og lagre værdata fra Frost API.

### `test_predictions.py`
Tester prediksjonsmodulen for å lese data, resample, trene modeller og lage prediksjoner.

### `test_data_processing.py`
Tester funksjoner for databehandling som rensing, resampling og fylling av manglende verdier.

## Kjøre tester

1. Installer nødvendige avhengigheter (`pandas`, `numpy`, `scikit-learn`, osv.).
2. Kjør testene med:
   ```bash
   python -m unittest discover -s tests -p "*.py"
   ```

## Struktur

- **`src/`**: Kildekode.
- **`tests/`**: Testfiler.

Legg til nye tester ved å opprette en fil i `tests/` og følge eksisterende struktur.
