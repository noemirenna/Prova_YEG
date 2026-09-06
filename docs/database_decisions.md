# Decisioni di progettazione

## Perché non copiare direttamente l'Excel

Il file Excel contiene molte colonne ripetitive e strutture poco adatte alle interrogazioni.
Copiare il foglio così com'è nel database renderebbe più difficile filtrare, confrontare e collegare i dati.
Per questo il contenuto viene riorganizzato in tabelle più adatte all'uso analitico.

## Normalizzazione

La normalizzazione serve a separare i dati ripetuti in entità dedicate.
Le regioni ripetute diventano una tabella.
Gli stakeholder ripetuti diventano una tabella.
I canali ripetuti diventano una tabella.
I touchpoint vengono separati dalla tabella principale per descrivere meglio le fasi e i contatti del congresso.

## Gestione dei valori vuoti

Le celle vuote non sempre significano zero.
In molti casi indicano solo che l'informazione non è presente nel file di partenza.
Per questo i valori mancanti vengono mantenuti come NULL quando rappresentano un'informazione assente.

## Date

Le date italiane verranno convertite in un formato coerente durante l'importazione.
Questo evita ambiguità e rende più semplice ordinare, filtrare e confrontare i record.

## Obiettivo finale

Il modello è pensato per rendere semplici le API e la dashboard.