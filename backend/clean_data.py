"""Pulizia in memoria del dataset del congresso.

Non modifica il file .ods e non scrive nel database.
Ogni funzione esegue una sola operazione e restituisce
anche il numero di modifiche, usato nel report finale.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Permette di eseguire lo script sia dalla root sia da backend/.
percorso_backend = Path(__file__).resolve().parent
if str(percorso_backend) not in sys.path:
    sys.path.insert(0, str(percorso_backend))

from import_dataset import load_dataset

PATTERN_DATA_ITALIANA = re.compile(r"\d{1,2}/\d{1,2}/\d{4}")

# Si toglie il "2" incoerente (presente solo su alcuni header)
# e si espande l'abbreviazione "interaz." in "interazione".
MAPPA_COLONNE_LINKEDIN = {
    "Linkedin_annuncio_-_reach": "linkedin_annuncio_reach",
    "Linkedin_2_annuncio_-_interaz.": "linkedin_annuncio_interazione",
    "Linkedin_2_recap_-_reach": "linkedin_recap_reach",
    "Linkedin_2_recap_-_interaz.": "linkedin_recap_interazione",
}

MAPPA_BOOLEANI = {
    "sì": True,
    "si": True,
    "no": False,
}


def normalize_column_names(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Rimuove gli spazi extra e sostituisce gli spazi con underscore.

    Args:
        df: DataFrame con intestazioni ancora grezze.

    Returns:
        DataFrame con nomi colonna normalizzati e numero di colonne rinominate.
    """
    tabella = df.copy()
    nuovi_nomi = []
    colonne_rinominate = 0
    for nome_originale in tabella.columns:
        nome_pulito = str(nome_originale).strip()
        nome_pulito = nome_pulito.replace(" ", "_")
        nuovi_nomi.append(nome_pulito)
        if nome_pulito != str(nome_originale):
            colonne_rinominate += 1
    tabella.columns = nuovi_nomi
    return tabella, colonne_rinominate


def _nome_linkedin_fallback(nome_colonna: str) -> str:
    """Semplifica trattini e punti senza togliere il significato."""
    nome_semplificato = nome_colonna.replace("_-_", "_")
    nome_semplificato = nome_semplificato.replace("-", "_")
    nome_semplificato = nome_semplificato.replace(".", "")
    return nome_semplificato.lower()


def clean_linkedin_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Rende coerenti le intestazioni LinkedIn incoerenti.

    Args:
        df: DataFrame con nomi colonna già normalizzati.

    Returns:
        DataFrame con header LinkedIn allineati e numero di colonne rinominate.
    """
    tabella = df.copy()
    nuovi_nomi = []
    colonne_rinominate = 0
    for nome_originale in tabella.columns:
        if "linkedin" not in str(nome_originale).lower():
            nuovi_nomi.append(nome_originale)
            continue
        nome_nuovo = MAPPA_COLONNE_LINKEDIN.get(nome_originale)
        if nome_nuovo is None:
            nome_nuovo = _nome_linkedin_fallback(str(nome_originale))
        nuovi_nomi.append(nome_nuovo)
        if nome_nuovo != nome_originale:
            colonne_rinominate += 1
    tabella.columns = nuovi_nomi
    return tabella, colonne_rinominate


def _valore_e_vuoto(valore: object) -> bool:
    """True se la cella è vuota e va convertita in None."""
    if valore is None:
        return False
    try:
        if pd.isna(valore):
            return True
    except (ValueError, TypeError):
        pass
    if isinstance(valore, str) and valore.strip() == "":
        return True
    return False


def replace_empty_values(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Converte celle vuote e stringhe vuote in None, senza usare zero.

    Args:
        df: DataFrame da ripulire.

    Returns:
        DataFrame con i vuoti come None e numero di celle convertite.
    """
    tabella = df.copy()
    celle_convertite = 0
    for nome_colonna in tabella.columns:
        nuova_colonna = []
        for valore in tabella[nome_colonna]:
            if _valore_e_vuoto(valore):
                nuova_colonna.append(None)
                celle_convertite += 1
            else:
                nuova_colonna.append(valore)
        tabella[nome_colonna] = pd.Series(nuova_colonna, dtype=object)
    return tabella, celle_convertite


def _nome_sembra_colonna_data(nome_colonna: str) -> bool:
    """Controlla se il nome colonna indica una data (token interi)."""
    parti = nome_colonna.lower().replace("-", "_").split("_")
    if "giorno" in parti:
        return True
    if "data" in parti:
        return True
    if "date" in parti:
        return True
    return False


def _colonna_contiene_date(nome_colonna: str, serie: pd.Series) -> bool:
    """True se la colonna è data per nome o per formato italiano."""
    if _nome_sembra_colonna_data(nome_colonna):
        return True
    for valore in serie:
        if not isinstance(valore, str):
            continue
        if PATTERN_DATA_ITALIANA.fullmatch(valore.strip()):
            return True
    return False


def _converti_valore_data(valore: object) -> object:
    """Converte una data italiana; lascia invariato ciò che non è convertibile."""
    if valore is None:
        return valore
    if isinstance(valore, datetime):
        return valore
    testo = str(valore).strip()
    try:
        return datetime.strptime(testo, "%d/%m/%Y")
    except ValueError:
        return valore


def convert_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Converte le date italiane in datetime nelle colonne di tipo data.

    Args:
        df: DataFrame con eventuali date come stringa.

    Returns:
        DataFrame con date convertite e numero di celle convertite.
    """
    tabella = df.copy()
    date_convertite = 0
    for nome_colonna in tabella.columns:
        if not _colonna_contiene_date(str(nome_colonna), tabella[nome_colonna]):
            continue
        nuova_colonna = []
        for valore in tabella[nome_colonna]:
            valore_convertito = _converti_valore_data(valore)
            if valore_convertito is not valore and isinstance(
                valore_convertito, datetime
            ):
                date_convertite += 1
            nuova_colonna.append(valore_convertito)
        tabella[nome_colonna] = pd.Series(nuova_colonna, dtype=object)
    return tabella, date_convertite


def _converti_valore_booleano(valore: object) -> tuple[object, bool]:
    """Converte Sì/Si/No in True/False; non tocca gli altri valori."""
    if not isinstance(valore, str):
        return valore, False
    chiave = valore.strip().lower()
    if chiave not in MAPPA_BOOLEANI:
        return valore, False
    return MAPPA_BOOLEANI[chiave], True


def clean_booleans(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Converte le stringhe Sì/Si/No in booleani Python.

    Non modifica i flag numerici 0/1 né le altre colonne.

    Args:
        df: DataFrame da ispezionare.

    Returns:
        DataFrame con booleani convertiti e numero di celle convertite.
    """
    tabella = df.copy()
    booleani_convertiti = 0
    for nome_colonna in tabella.columns:
        nuova_colonna = []
        for valore in tabella[nome_colonna]:
            nuovo_valore, convertito = _converti_valore_booleano(valore)
            if convertito:
                booleani_convertiti += 1
            nuova_colonna.append(nuovo_valore)
        tabella[nome_colonna] = pd.Series(nuova_colonna, dtype=object)
    return tabella, booleani_convertiti


def count_renamed_columns(
    colonne_originali: pd.Index, colonne_finali: pd.Index
) -> int:
    """Conta quante colonne hanno un nome finale diverso dall'originale.

    Il confronto è posizionale: ogni indice rappresenta la stessa colonna
    lungo tutta la pipeline di rinomina.

    Args:
        colonne_originali: Intestazioni iniziali del foglio.
        colonne_finali: Intestazioni dopo tutte le rinomine.

    Returns:
        Numero di colonne uniche effettivamente rinominate.
    """
    colonne_rinominate = 0
    for nome_originale, nome_finale in zip(colonne_originali, colonne_finali):
        if str(nome_originale) != str(nome_finale):
            colonne_rinominate += 1
    return colonne_rinominate


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Applica tutta la pipeline di pulizia nell'ordine previsto.

    Args:
        df: DataFrame grezzo.

    Returns:
        DataFrame pulito e dizionario con i conteggi delle modifiche.
    """
    tabella = df.copy()
    colonne_originali = tabella.columns.copy()
    tabella, _colonne_nomi = normalize_column_names(tabella)
    tabella, colonne_linkedin = clean_linkedin_columns(tabella)
    colonne_rinominate_uniche = count_renamed_columns(
        colonne_originali, tabella.columns
    )
    tabella, celle_vuote = replace_empty_values(tabella)
    tabella, date_convertite = convert_dates(tabella)
    tabella, _booleani_convertiti = clean_booleans(tabella)
    report = {
        "celle_vuote_convertite": celle_vuote,
        "date_convertite": date_convertite,
        "colonne_rinominate": colonne_rinominate_uniche,
        "linkedin_rinominate": colonne_linkedin,
    }
    return tabella, report


def main() -> None:
    """Pulisce i due fogli in memoria e stampa un piccolo report."""
    interazioni_df, partecipanti_df = load_dataset()
    interazioni_pulite, report_interazioni = clean_dataset(interazioni_df)
    partecipanti_puliti, report_partecipanti = clean_dataset(partecipanti_df)

    print("Foglio 01_Interazioni")
    print(
        f"  righe={interazioni_pulite.shape[0]}, "
        f"colonne={interazioni_pulite.shape[1]}"
    )
    print(f"  report={report_interazioni}")
    print("Foglio 02_Partecipanti")
    print(
        f"  righe={partecipanti_puliti.shape[0]}, "
        f"colonne={partecipanti_puliti.shape[1]}"
    )
    print(f"  report={report_partecipanti}")


if __name__ == "__main__":
    main()
