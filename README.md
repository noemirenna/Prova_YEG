# Congresso 2025

Prova tecnica per YEG dedicata allo sviluppo di una piccola applicazione data-oriented per l'analisi di un congresso medico.
Il progetto importa i dati da un file ODS in PostgreSQL, li espone tramite API FastAPI e li visualizza in una dashboard HTML, CSS e JavaScript.

## Tecnologie utilizzate

- Python e FastAPI per il backend
- PostgreSQL 16 per il database relazionale
- Docker Compose per avviare database e API
- HTML, CSS e JavaScript con Chart.js per il frontend
- Pandas e `odfpy` per leggere il file ODS

## Come avviare il progetto

Clonare il repository:

```bash
git clone https://github.com/noemirenna/Prova_YEG.git
cd Prova_YEG
```

Creare il file delle variabili d'ambiente:

```bash
cp .env.example .env
```

Su Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Il dataset non viene versionato. Inserire il file `Dataset Evento Congresso 2025.ods` nella cartella `data/`:

```text
data/Dataset Evento Congresso 2025.ods
```

Avviare PostgreSQL e il backend:

```bash
docker compose up --build
```

Quando il backend è avviato, aprire un secondo terminale ed eseguire il comando per importare il dataset nel database.

```bash
docker compose run --rm -v "${PWD}/data:/data" backend python scripts/import_data.py
```

Su PowerShell si può usare lo stesso comando con `${PWD}`.
Il frontend è composto da file HTML, CSS e JavaScript statici, quindi va avviato separatamente con il server HTTP di Python:

```bash
python -m http.server 5500 --directory frontend
```

Gli indirizzi sono:

- dashboard: http://localhost:5500/
- API: http://localhost:8000/
- documentazione interattiva FastAPI: http://localhost:8000/docs

Le principali route API sono `/participants`, `/dashboard/funnel`, `/dashboard/stakeholders` e `/dashboard/daily`.

## Scelte tecniche

- **PostgreSQL:** è adatto a dati relazionali con vincoli, chiavi esterne e query di aggregazione. È più ordinato di mantenere tutto nel foglio ODS.
- **FastAPI:** permette di creare endpoint REST in modo semplice e offre la documentazione Swagger automaticamente.
- **Docker:** rende più riproducibili l'ambiente PostgreSQL e l'avvio del backend, senza installare il database direttamente sul computer.
- **Alternativa considerata:** usare direttamente Pandas e un database SQLite. È stata scartata perché PostgreSQL rappresenta meglio relazioni, vincoli e un possibile uso multiutente.

## Modello dati

La tabella `participants` contiene i dati anagrafici. Regioni, stakeholder e canali sono tabelle di riferimento separate. I touchpoint sono descritti in `touchpoints`; la tabella `participant_touchpoints` collega ogni partecipante ai touchpoint e conserva il valore nel tipo corretto (booleano, intero, decimale o data).

Schema semplificato:

```text
participants 1 --- N participant_touchpoints N --- 1 touchpoints
	|
	+--- region / stakeholder_type / engagement_channel
```

Questa normalizzazione riduce la ripetizione di valori come regioni e categorie e rende più semplici le query analitiche.

## Pulizia del dataset

Lo script `backend/scripts/import_data.py` gestisce le anomalie presenti nel flusso di importazione:

- celle vuote o composte solo da spazi convertite in `NULL`;
- separazione di nome e cognome dalla colonna unica del dataset;
- conversione delle date nel formato usato da PostgreSQL;
- conversione dei valori booleani, numerici e decimali nei tipi previsti;
- uniformazione delle fasi e dei tipi di dato dei touchpoint;
- esclusione della riga `Anagrafica` dal catalogo dei touchpoint;
- inserimento delle regioni, categorie e canali in tabelle lookup senza duplicati.

## Cosa mostra la dashboard

La dashboard mostra un funnel con raggiunti, visite allo stand, accessi alla sala VIP e presenze al simposio; un confronto dei partecipanti per categoria di stakeholder; e l'andamento giornaliero delle visite. L'interfaccia include un filtro globale per Regione. Al momento, però, le route `/dashboard/*` non ricevono ancora questo parametro, quindi i tre grafici non vengono aggiornati. Questo rappresenta un limite dell'implementazione attuale.

## Tre osservazioni sui dati

Le osservazioni derivano dal dataset locale analizzato durante la prova. I valori riportati fanno riferimento ai dati del file ODS utilizzato per l'importazione:

1. Sono presenti 2.375 partecipanti; 1.846 hanno `Database DEM` come canale di ingaggio, quindi è il canale nettamente più rappresentato.
2. Le visite allo stand sono 168, gli accessi alla sala VIP 61 e le presenze al simposio 96. I conteggi descrivono touchpoint distinti e non sono necessariamente un funnel cumulativo.
3. Le visite registrate per giorno sono 64 il 15 ottobre, 72 il 16 ottobre, 25 il 17 ottobre e 7 il 18 ottobre 2025: il picco è quindi il 16 ottobre.

## Limiti

Il dataset è una fotografia dell'evento e non ha permesso di dimostrare che un canale abbia causato una maggiore partecipazione. I risultati mostrano associazioni tra i dati, ma non un rapporto di causa-effetto. Mancano inoltre informazioni come costi, campagne complete, informazioni sufficienti per identificare con certezza eventuali duplicati e contesto temporale oltre alle date disponibili. Il file ODS è locale e non è incluso nel repository; senza importazione il database resta vuoto. Il filtro Regione della dashboard deve ancora essere collegato alle query dei grafici.

## Miglioramenti futuri

- collegare il filtro Regione a tutte le route della dashboard;
- aggiungere test automatici per importazione, API e query principali;
- aggiungere autenticazione;
- aggiungere filtri aggiuntivi;
