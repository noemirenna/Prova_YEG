from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StakeholderType(Base):
    __tablename__ = "stakeholder_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class EngagementChannel(Base):
    __tablename__ = "engagement_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    stakeholder_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("stakeholder_types.id")
    )
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"))
    engagement_channel_id: Mapped[int | None] = mapped_column(
        ForeignKey("engagement_channels.id")
    )

    stakeholder_type: Mapped[StakeholderType | None] = relationship()
    region: Mapped[Region | None] = relationship()
    engagement_channel: Mapped[EngagementChannel | None] = relationship()