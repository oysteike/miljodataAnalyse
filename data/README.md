# Værdata for Norge
I denne folderen finner du all data vi har hentet inn. Samtlige filer er lagret som csv, filer. De er kommaseparert og lett å lese.
## Datastruktur

### oslo_2015-2025/
- `Humidity.csv`,`Precipitation.csv`,`Pressure.csv`,`Sunshine.csv`,`Temperature.csv`,`Wind.csv` (brukt til sammenligning og predikjson)

### Jan_2025/
 - Værdata for januar 2025 alle målinger i Norge (brukt til heatmap)

### temperature_since_2015/
 - Temperaturdata fra 2015 alle målinger i Norge (brukt til å vurdere temperaturstinging)

### outliers/
 - Avvikende verdier som har blitt fjernet fra de mindre bachene med data.
 NB: inneholder ikke outliers fra de større datasettene, da dette ikke er like intressant når vi evaluerer større datasett. 

### Verstasjoner/
 - Værstasjonene i Norge, med deres plassering.

---

## Tips
For å visualisere dataene dine med regnbuefarger i CSV-filene, kan du laste ned programmet `rainbow-csv` (tilgjengelig som plugin for de fleste teksteditorer, f.eks. VS Code). Dette gjør det enklere å lese og analysere dataene.

