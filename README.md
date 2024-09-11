# Thesis_WebRTC

Questa repository contiene tutti i file e le risorse utilizzate per il mio lavoro di tesi riguardante i test di streaming video peer-to-peer tramite WebRTC. I test sono stati realizzati utilizzando infrastrutture personalizzate, script Python e pagine web interattive per simulare e monitorare la qualità dello streaming.

## Struttura delle directory

- **data/**: Contiene i dati raccolti durante i test di WebRTC, inclusi report sulle prestazioni e utilizzo delle risorse. Questa directory è organizzata per tipologia di dati, con i risultati di ogni test numerati in maniera progressiva.

- **graphics/**: Include gli script utilizzati per generare i grafici. Questi grafici rappresentano metriche di performance come l'utilizzo della CPU, la latenza e la qualità dello streaming.

- **infrastructures/**: Qui sono presenti gli script e i file di configurazione di supporto necessari per il corretto funzionamento del test (websocket e webserver).

- **tests/**: Contiene gli script Python per l'esecuzione dei test automatizzati, in particolare quelli che simulano l'interazione tra il sender e il receiver tramite WebRTC, utilizzando Playwright per controllare i browser.

- **webpages/**: Include le pagine web utilizzate durante i test. In particolare una pagina sender ed una receiver che collaborano per eseguire una prova di streaming video.

## ⚠️ Avviso Importante

Se si volessero testare i file presenti, bisogna assicurarsi di verificare quanto segue:
- Gli **indirizzi IP** configurati negli script devono corrispondere ai dispositivi o server che utilizzi per i test.
- Controlla che i **percorsi dei file** specificati negli script siano corretti e accessibili.

Ignorare questi dettagli potrebbe causare il fallimento dei test o risultati non validi.

## Come iniziare

1. Clona questa repository:
   ```bash
   git clone https://github.com/federico53/Thesis_WebRTC.git
