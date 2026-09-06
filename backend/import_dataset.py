"""Caricamento del dataset del congresso da file tabellare.

Questo modulo conterrà la lettura del file .ods e la selezione
dei fogli. La logica di importazione non è ancora implementata.
"""

from pathlib import Path

import pandas as pd


def carica_dataset(percorso_file: Path) -> pd.DataFrame:
    """Carica il dataset dal percorso indicato.

    Args:
        percorso_file: Percorso del file .ods (o altro formato tabellare).

    Returns:
        DataFrame con i dati grezzi del file.
    """
    pass


def seleziona_foglio(percorso_file: Path, nome_foglio: str) -> pd.DataFrame:
    """Seleziona un foglio specifico dal file del dataset.

    Args:
        percorso_file: Percorso del file .ods.
        nome_foglio: Nome del foglio da leggere.

    Returns:
        DataFrame con i dati del foglio richiesto.
    """
    pass


def main() -> None:
    """Punto di ingresso per il caricamento del dataset."""
    pass


if __name__ == "__main__":
    main()
