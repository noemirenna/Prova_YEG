from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.participant import (
    EngagementChannel,
    Participant,
    Region,
    StakeholderType,
)
from app.schemas import ParticipantResponse, ParticipantsResponse

router = APIRouter()


@router.get("/participants", response_model=ParticipantsResponse)
async def get_participants(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    region: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Restituisce una pagina di partecipanti e il totale filtrato."""
    base_query = (
        select(Participant, StakeholderType.name, Region.name, EngagementChannel.name)
        .outerjoin(StakeholderType, Participant.stakeholder_type_id == StakeholderType.id)
        .outerjoin(Region, Participant.region_id == Region.id)
        .outerjoin(
            EngagementChannel,
            Participant.engagement_channel_id == EngagementChannel.id,
        )
    )

    if region:
        base_query = base_query.where(Region.name == region)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = await db.scalar(count_query)
    result = await db.execute(base_query.offset(offset).limit(limit))

    participants = []
    for participant, stakeholder, region_name, channel in result.all():
        participants.append(
            ParticipantResponse(
                first_name=participant.first_name,
                last_name=participant.last_name,
                email=participant.email,
                stakeholder=stakeholder,
                region=region_name,
                engagement_channel=channel,
            )
        )

    return ParticipantsResponse(
        total=total or 0,
        limit=limit,
        offset=offset,
        participants=participants,
    )