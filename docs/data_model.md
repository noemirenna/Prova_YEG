# Modello dati

Questo progetto parte da un file Excel con informazioni sul congresso e le trasforma in un database relazionale.
L’obiettivo è rendere i dati più ordinati, coerenti e facili da interrogare rispetto al foglio originale.
Il modello separa le informazioni anagrafiche dalle relazioni operative tra partecipanti, interazioni e touchpoint.
In questo modo diventa più semplice analizzare il comportamento dei partecipanti lungo tutto il congresso.

## Obiettivo

Il file Excel viene trasformato in un database PostgreSQL più facile da interrogare.
La struttura relazionale permette di evitare duplicazioni inutili e di collegare i dati in modo chiaro.
Ogni entità ha un ruolo preciso e contribuisce a rendere le analisi più affidabili.

## Entità principali

| Entità | Scopo | Chiave principale | Perché esiste |
| --- | --- | --- | --- |
| Partecipante | Rappresenta ogni persona censita nel dataset. | `id_partecipante` | Serve come punto centrale per collegare regione, stakeholder, canale e interazioni. |
| Regione | Descrive l’area geografica associata al partecipante. | `id_regione` | Permette analisi territoriali e confronti tra diverse aree. |
| Stakeholder | Identifica il tipo di soggetto o profilo del partecipante. | `id_stakeholder` | Consente di raggruppare i partecipanti per categoria e confrontare i comportamenti. |
| Canale | Indica il canale di provenienza o relazione del partecipante. | `id_canale` | Serve per studiare l’origine dei partecipanti e il peso dei diversi canali. |
| Touchpoint | Rappresenta una fase, un momento o un contatto del congresso. | `id_touchpoint` | Permette di organizzare le interazioni lungo il percorso dell’evento. |
| Interazione | Registra ogni azione o contatto osservato sul partecipante. | `id_interazione` | È la tabella operativa usata per analizzare i comportamenti nel tempo. |

## Relazioni

Un partecipante appartiene a una regione, quindi ogni persona è collegata a un solo contesto geografico di riferimento.
Un partecipante appartiene anche a un tipo di stakeholder, che descrive il suo profilo all’interno del congresso.
Allo stesso modo, un partecipante appartiene a un canale, che ne indica la provenienza o il percorso di ingresso.
Un partecipante può avere molte interazioni, perché nel corso del congresso può compiere più azioni o ricevere più contatti.
Un touchpoint può essere associato a molte interazioni, perché la stessa fase del congresso può coinvolgere più partecipanti o più eventi.

Questo modello consente di costruire funnel, confronti per regione e analisi delle fasi del congresso in modo semplice e coerente.