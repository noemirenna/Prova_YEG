from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import DashboardFunnelResponse

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