"""Lettura del dataset del congresso dal file .ods.

Carica i fogli Interazioni e Partecipanti senza pulire i dati
e senza importarli nel database.
"""

from pathlib import Path

import pandas as pd

# Percorso del file rispetto alla root del repository.
PERCORSO_DATASET = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "Dataset Evento Congresso 2025.ods"
)

FOGLIO_INTERAZIONI = "01_Interazioni"
FOGLIO_PARTECIPANTI = "02_Partecipanti"


def seleziona_foglio(percorso_file: Path, nome_foglio: str) -> pd.DataFrame:
    """Legge un foglio del file .ods e lo restituisce come DataFrame.

    Args:
        percorso_file: Percorso del file .ods.
        nome_foglio: Nome del foglio da leggere.

    Returns:
        DataFrame grezzo del foglio richiesto.
    """
    tabella = pd.read_excel(
        percorso_file,
        sheet_name=nome_foglio,
        engine="odf",
    )
    return tabella


def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carica i due fogli del dataset congresso.

    Returns:
        Coppia (interazioni_df, partecipanti_df).

    Raises:
        FileNotFoundError: Se il file .ods non esiste.
    """
    if not PERCORSO_DATASET.exists():
        raise FileNotFoundError(
            f"File del dataset non trovato: {PERCORSO_DATASET}"
        )

    interazioni_df = seleziona_foglio(PERCORSO_DATASET, FOGLIO_INTERAZIONI)
    partecipanti_df = seleziona_foglio(PERCORSO_DATASET, FOGLIO_PARTECIPANTI)
    return interazioni_df, partecipanti_df


def main() -> None:
    """Carica i fogli e stampa solo dimensioni e nomi."""
    try:
        interazioni_df, partecipanti_df = load_dataset()
    except FileNotFoundError as errore:
        print(f"Errore: {errore}")
        return
    except Exception as errore_lettura:
        print(f"Errore di lettura del dataset: {errore_lettura}")
        return

    print(f"Fogli caricati: {FOGLIO_INTERAZIONI}, {FOGLIO_PARTECIPANTI}")
    print(
        f"{FOGLIO_INTERAZIONI}: "
        f"{interazioni_df.shape[0]} righe, "
        f"{interazioni_df.shape[1]} colonne"
    )
    print(
        f"{FOGLIO_PARTECIPANTI}: "
        f"{partecipanti_df.shape[0]} righe, "
        f"{partecipanti_df.shape[1]} colonne"
    )


if __name__ == "__main__":
    main()
