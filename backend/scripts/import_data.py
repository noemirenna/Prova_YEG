"""Importa i partecipanti del congresso nel database PostgreSQL."""

from pathlib import Path
import os

import pandas as pd
import psycopg2


# Il file si trova nella cartella data della root del progetto.
PERCORSO_DATASET = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "Dataset Evento Congresso 2025.ods"
)
NOME_FOGLIO = "02_Partecipanti"


def valore_o_none(valore):
    """Restituisce None per le celle vuote, utile per PostgreSQL NULL."""
    if pd.isna(valore) or (isinstance(valore, str) and not valore.strip()):
        return None
    return valore.strip() if isinstance(valore, str) else valore


def carica_partecipanti():
    """Legge e prepara il foglio dei partecipanti."""
    tabella = pd.read_excel(
        PERCORSO_DATASET,
        sheet_name=NOME_FOGLIO,
        engine="odf",
    )

    colonne_richieste = {
        "Nome e cognome": "full_name",
        "Email (chiave)": "email",
        "Tipologia stakeholder": "stakeholder_type",
        "Regione": "region",
        "Canale di ingaggio": "engagement_channel",
    }
    colonne_mancanti = set(colonne_richieste) - set(tabella.columns)
    if colonne_mancanti:
        raise ValueError(
            "Colonne mancanti nel foglio 02_Partecipanti: "
            + ", ".join(sorted(colonne_mancanti))
        )

    tabella = tabella.rename(columns=colonne_richieste)

    # Il file contiene nome e cognome nella stessa colonna.
    nomi = tabella["full_name"].map(valore_o_none)
    tabella["first_name"] = nomi.map(
        lambda valore: valore.split(" ", 1)[0] if valore else None
    )
    tabella["last_name"] = nomi.map(
        lambda valore: valore.split(" ", 1)[1] if valore and " " in valore else None
    )
    return tabella


def inserisci_lookup(cursor, tabella, valori):
    """Inserisce i valori unici e restituisce una mappa valore -> ID."""
    for valore in sorted({valore for valore in valori if valore is not None}):
        cursor.execute(
            f"""
            INSERT INTO {tabella} (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """,
            (valore,),
        )

    cursor.execute(f"SELECT id, name FROM {tabella}")
    return {nome: identificativo for identificativo, nome in cursor.fetchall()}


def inserisci_touchpoints(cursor):
    """Punto di estensione per il futuro import in participant_touchpoints."""
    # In seguito qui si potranno collegare i valori del foglio 01_Interazioni.
    pass


def importa_dati():
    """Legge il dataset e importa lookup e partecipanti in una transazione."""
    partecipanti = carica_partecipanti()
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/congresso_db",
    )

    # La transazione viene confermata solo se tutte le insert terminano bene.
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cursor:
            stakeholder_ids = inserisci_lookup(
                cursor,
                "stakeholder_types",
                (valore_o_none(valore) for valore in partecipanti["stakeholder_type"]),
            )
            region_ids = inserisci_lookup(
                cursor,
                "regions",
                (valore_o_none(valore) for valore in partecipanti["region"]),
            )
            channel_ids = inserisci_lookup(
                cursor,
                "engagement_channels",
                (valore_o_none(valore) for valore in partecipanti["engagement_channel"]),
            )

            # Inserisce ogni partecipante usando gli ID delle tabelle lookup.
            for _, riga in partecipanti.iterrows():
                stakeholder = valore_o_none(riga["stakeholder_type"])
                regione = valore_o_none(riga["region"])
                canale = valore_o_none(riga["engagement_channel"])
                cursor.execute(
                    """
                    INSERT INTO participants (
                        email, first_name, last_name,
                        stakeholder_type_id, region_id, engagement_channel_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    """,
                    (
                        valore_o_none(riga["email"]),
                        valore_o_none(riga["first_name"]),
                        valore_o_none(riga["last_name"]),
                        stakeholder_ids.get(stakeholder),
                        region_ids.get(regione),
                        channel_ids.get(canale),
                    ),
                )

            inserisci_touchpoints(cursor)

    print(f"Import completato: {len(partecipanti)} righe elaborate.")


if __name__ == "__main__":
    importa_dati()