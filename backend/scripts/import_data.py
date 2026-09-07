"""Importa i partecipanti del congresso nel database PostgreSQL."""

from pathlib import Path
import os
from datetime import datetime

import pandas as pd
import psycopg2


# Il file si trova nella cartella data della root del progetto.
PERCORSO_DATASET = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "Dataset Evento Congresso 2025.ods"
)
NOME_FOGLIO = "02_Partecipanti"
NOME_FOGLIO_TOUCHPOINT = "01_Interazioni"


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


def carica_touchpoints():
    """Legge il catalogo dei touchpoint dal foglio delle interazioni."""
    touchpoints = pd.read_excel(
        PERCORSO_DATASET,
        sheet_name=NOME_FOGLIO_TOUCHPOINT,
        engine="odf",
    )
    return touchpoints[touchpoints["Fase del percorso"] != "Anagrafica"]


def normalizza_fase(fase):
    """Converte la fase del dataset nel valore previsto dal database."""
    fase = fase.lower()
    if fase.startswith("pre-evento"):
        return "pre_event"
    if fase.startswith("on-site"):
        return "on_site"
    if fase.startswith("sessione"):
        return "session"
    if fase.startswith("post-evento"):
        return "post_event"
    raise ValueError(f"Fase non riconosciuta: {fase}")


def normalizza_tipo(tipo):
    """Converte il tipo del dataset nel valore previsto dal database."""
    if tipo == "booleano":
        return "boolean"
    if tipo == "conteggio" or tipo == "minuti":
        return "integer"
    if tipo == "tasso da 0 a 1":
        return "decimal"
    if tipo == "data":
        return "date"
    raise ValueError(f"Tipo di dato non riconosciuto: {tipo}")


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


def inserisci_touchpoints(cursor, touchpoints):
    """Inserisce i touchpoint e restituisce la mappa codice -> ID."""
    for _, touchpoint in touchpoints.iterrows():
        tipo = normalizza_tipo(touchpoint["Tipo di dato"])
        cursor.execute(
            """
            INSERT INTO touchpoints (code, source_column, name, phase, data_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET
                source_column = EXCLUDED.source_column,
                name = EXCLUDED.name,
                phase = EXCLUDED.phase,
                data_type = EXCLUDED.data_type
            """,
            (
                touchpoint["Nome tecnico"],
                touchpoint["Intestazione nel foglio 02"],
                touchpoint["Intestazione nel foglio 02"],
                normalizza_fase(touchpoint["Fase del percorso"]),
                tipo,
            ),
        )

    cursor.execute("SELECT id, code FROM touchpoints")
    return {code: touchpoint_id for touchpoint_id, code in cursor.fetchall()}


def valore_touchpoint(valore, tipo):
    """Prepara un valore per la colonna corretta di participant_touchpoints."""
    valore = valore_o_none(valore)
    if valore is None:
        return None
    if tipo == "booleano":
        return str(valore).strip().lower() in {"1", "1.0", "si", "sì", "true"}
    if tipo in {"conteggio", "minuti"}:
        return int(valore)
    if tipo == "data":
        if hasattr(valore, "date"):
            return valore.date()
        return datetime.strptime(str(valore), "%d/%m/%Y").date()
    return valore


def inserisci_valori_touchpoints(cursor, partecipanti, touchpoints, touchpoint_ids):
    """Collega i valori presenti dei partecipanti ai relativi touchpoint."""
    cursor.execute("SELECT id, email FROM participants")
    participant_ids = {email: participant_id for participant_id, email in cursor.fetchall()}

    for _, partecipante in partecipanti.iterrows():
        participant_id = participant_ids.get(valore_o_none(partecipante["email"]))
        if participant_id is None:
            continue

        for _, touchpoint in touchpoints.iterrows():
            valore = valore_touchpoint(
                partecipante[touchpoint["Intestazione nel foglio 02"]],
                touchpoint["Tipo di dato"],
            )
            if valore is None:
                continue

            tipo = normalizza_tipo(touchpoint["Tipo di dato"])
            valori = {
                "value_boolean": valore if tipo == "boolean" else None,
                "value_integer": valore if tipo == "integer" else None,
                "value_decimal": valore if tipo == "decimal" else None,
                "value_date": valore if tipo == "date" else None,
            }
            cursor.execute(
                """
                INSERT INTO participant_touchpoints (
                    participant_id, touchpoint_id, value_boolean,
                    value_integer, value_decimal, value_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (participant_id, touchpoint_id) DO UPDATE SET
                    value_boolean = EXCLUDED.value_boolean,
                    value_integer = EXCLUDED.value_integer,
                    value_decimal = EXCLUDED.value_decimal,
                    value_date = EXCLUDED.value_date
                """,
                (
                    participant_id,
                    touchpoint_ids[touchpoint["Nome tecnico"]],
                    valori["value_boolean"],
                    valori["value_integer"],
                    valori["value_decimal"],
                    valori["value_date"],
                ),
            )


def importa_dati():
    """Legge il dataset e importa lookup e partecipanti in una transazione."""
    partecipanti = carica_partecipanti()
    touchpoints = carica_touchpoints()
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

            touchpoint_ids = inserisci_touchpoints(cursor, touchpoints)
            inserisci_valori_touchpoints(
                cursor, partecipanti, touchpoints, touchpoint_ids
            )

    print(f"Import completato: {len(partecipanti)} righe elaborate.")


if __name__ == "__main__":
    importa_dati()