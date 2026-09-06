# Cardinalità

| Tabella A    | Relazione | Tabella B    |
| ------------ | --------- | ------------ |
| Regione      | 1:N       | Partecipante |
| Stakeholder  | 1:N       | Partecipante |
| Canale       | 1:N       | Partecipante |
| Partecipante | 1:N       | Interazione  |
| Touchpoint   | 1:N       | Interazione  |

La relazione 1:N indica che un record della tabella A può essere collegato a molti record della tabella B.
Ogni record della tabella B, però, fa riferimento a un solo record della tabella A.
Questo schema è utile per rappresentare dati gerarchici e ridurre la duplicazione.
Nel progetto, permette di collegare in modo ordinato partecipanti, interazioni e riferimenti anagrafici.
