# Database schema

Il database finale organizza i dati del congresso in tabelle semplici e collegate tra loro.
Ogni tabella ha un ruolo preciso e contiene solo le informazioni utili alle analisi.
La struttura evita duplicazioni e rende i dati più facili da leggere, spiegare e interrogare.
Questo schema è pensato per supportare il lavoro di analisi, le API e la dashboard del progetto.

## participants

### Scopo

Contiene una sola volta le informazioni principali di ogni partecipante.
Serve come tabella centrale del modello perché collega i dati anagrafici alle attività svolte durante il congresso.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco del partecipante.
- `full_name`: nome completo del partecipante.
- `email`: indirizzo email del partecipante, con vincolo `UNIQUE`.
- `region_id`: riferimento alla regione associata.
- `stakeholder_id`: riferimento allo stakeholder associato.
- `channel_id`: riferimento al canale associato.

### Relazioni

- appartiene a una regione;
- appartiene a uno stakeholder;
- appartiene a un canale;
- può avere molte interazioni.

## regions

### Scopo

Raccoglie le regioni presenti nel dataset in una tabella dedicata.
Permette di riutilizzare lo stesso valore per più partecipanti senza duplicare le informazioni.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco della regione.
- `name`: nome della regione.

### Relazioni

- una regione può avere molti partecipanti.

## stakeholders

### Scopo

Contiene i tipi di stakeholder presenti nel progetto.
Serve per classificare i partecipanti in modo coerente e confrontabile.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco dello stakeholder.
- `type`: tipo di stakeholder.

### Relazioni

- uno stakeholder può avere molti partecipanti.

## channels

### Scopo

Contiene i canali di appartenenza o provenienza dei partecipanti.
Riduce la ripetizione degli stessi valori e rende più semplice filtrare e confrontare i dati.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco del canale.
- `name`: nome del canale.

### Relazioni

- un canale può avere molti partecipanti.

## touchpoints

### Scopo

Rappresenta il catalogo dei touchpoint ricavato dal foglio `01_Interazioni`.
Questa tabella deriva direttamente dal dizionario del dataset e descrive le colonne informative disponibili per le interazioni.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco del touchpoint.
- `technical_name`: nome tecnico del touchpoint.
- `data_type`: tipo di dato associato.
- `phase`: fase del percorso del congresso.
- `description`: descrizione del contenuto del touchpoint.

### Relazioni

- un touchpoint può comparire in molte interazioni.

## interactions

### Scopo

Registra le azioni compiute dai partecipanti durante il percorso del congresso.
Questa tabella contiene gli eventi osservati e collega ogni partecipante al touchpoint corrispondente.

### Chiave primaria

La chiave primaria è `id`.

### Colonne

- `id`: identificativo univoco dell'interazione.
- `participant_id`: riferimento al partecipante coinvolto.
- `touchpoint_id`: riferimento al touchpoint associato.
- `value`: valore registrato per il touchpoint (ad esempio true/false, un numero, una data o un testo, a seconda del tipo indicato nella tabella touchpoints).
- `event_date`: data dell'evento quando disponibile; può essere NULL se il touchpoint non prevede una data.

### Relazioni

- collega un partecipante a un touchpoint;
- permette di rappresentare le attività svolte durante il congresso.

## Conclusione

Il modello è stato progettato per evitare duplicazioni e mantenere i dati ordinati.
Le informazioni ripetitive (regioni, stakeholder e canali) sono state separate in tabelle dedicate, mentre il foglio `01_Interazioni` viene usato come catalogo dei touchpoint, così ogni evento fa riferimento a definizioni chiare e riutilizzabili.
Questa struttura semplifica le future query SQL, le API e la dashboard.
Permette anche di spiegare facilmente il flusso dei dati durante un colloquio tecnico.
