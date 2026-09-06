# Entity Relationship Diagram

```mermaid
erDiagram
    REGIONS ||--o{ PARTICIPANTS : "1:N"
    STAKEHOLDERS ||--o{ PARTICIPANTS : "1:N"
    CHANNELS ||--o{ PARTICIPANTS : "1:N"
    PARTICIPANTS ||--o{ INTERACTIONS : "1:N"
    TOUCHPOINTS ||--o{ INTERACTIONS : "1:N"

    REGIONS {
        int id PK
        string name
    }

    STAKEHOLDERS {
        int id PK
        string type
    }

    CHANNELS {
        int id PK
        string name
    }

    PARTICIPANTS {
        int id PK
        string full_name
        string email UNIQUE
        int region_id FK
        int stakeholder_id FK
        int channel_id FK
    }

    TOUCHPOINTS {
        int id PK
        string technical_name
        string data_type
        string phase
        string description
    }

    INTERACTIONS {
        int id PK
        int participant_id FK
        int touchpoint_id FK
        string value
        date event_date
    }
```

I partecipanti sono separati dalle interazioni perché descrivono due livelli diversi del modello: l’anagrafica del soggetto e gli eventi che lo riguardano.
Il foglio `01_Interazioni` è stato trasformato nella tabella `touchpoints` perché contiene il catalogo dei campi osservabili, non i valori dei singoli record.
In questo modo ogni interazione può riferirsi a un touchpoint già definito, evitando duplicazioni e rendendo i dati più coerenti.
Il modello è più semplice da interrogare perché collega in modo chiaro anagrafiche, catalogo degli eventi e osservazioni concrete.
Questo aiuta a costruire il funnel in maniera ordinata e a confrontare facilmente i risultati per regione, stakeholder e canale.
