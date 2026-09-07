from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.participant import Participant, StakeholderType
from app.schemas import DashboardFunnelResponse, StakeholderCountResponse

router = APIRouter()


@router.get("/dashboard/funnel", response_model=DashboardFunnelResponse)
async def get_dashboard_funnel(
    db: AsyncSession = Depends(get_db),
):
    query = text(
        """
        SELECT
            COUNT(DISTINCT p.id) AS reached,
            COUNT(DISTINCT CASE
                WHEN t.code = 'visita_stand'
                    AND pt.value_boolean IS TRUE
                THEN p.id
            END) AS stand,
            COUNT(DISTINCT CASE
                WHEN t.code = 'accesso_sala_vip'
                    AND pt.value_boolean IS TRUE
                THEN p.id
            END) AS reserved_room,
            COUNT(DISTINCT CASE
                WHEN t.code = 'presenza_simposio'
                    AND pt.value_boolean IS TRUE
                THEN p.id
            END) AS symposium
        FROM participants p
        LEFT JOIN participant_touchpoints pt ON pt.participant_id = p.id
        LEFT JOIN touchpoints t ON t.id = pt.touchpoint_id
        """
    )

    try:
        result = await db.execute(query)
        funnel = result.mappings().one()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error") from exc

    return DashboardFunnelResponse(**funnel)


@router.get(
    "/dashboard/stakeholders",
    response_model=list[StakeholderCountResponse],
)
async def get_dashboard_stakeholders(
    db: AsyncSession = Depends(get_db),
):
    count = func.count(Participant.id)
    query = (
        select(StakeholderType.name.label("stakeholder"), count.label("count"))
        .join(Participant, Participant.stakeholder_type_id == StakeholderType.id)
        .group_by(StakeholderType.name)
        .order_by(count.desc(), StakeholderType.name.asc())
    )

    try:
        result = await db.execute(query)
        stakeholders = result.mappings().all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error") from exc

    return [StakeholderCountResponse(**row) for row in stakeholders]