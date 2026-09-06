"""Modelli SQLAlchemy per il database del congresso.

Le colonne e le relazioni verranno definite dopo l'analisi dello schema.
Questo file contiene solo la struttura di base.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EventoCongresso(Base):
    """Modello placeholder per un evento del congresso.

    I campi (Column) verranno aggiunti quando lo schema dati sarà noto.
    """

    __tablename__ = "evento_congresso"

    pass


def main() -> None:
    """Punto di ingresso del modulo modelli.

    Non crea tabelle e non apre connessioni al database.
    """
    pass


if __name__ == "__main__":
    main()
