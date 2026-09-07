from datetime import date

from pydantic import BaseModel


class ParticipantResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    stakeholder: str | None = None
    region: str | None = None
    engagement_channel: str | None = None


class ParticipantsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    participants: list[ParticipantResponse]


class DashboardFunnelResponse(BaseModel):
    reached: int
    stand: int
    reserved_room: int
    symposium: int


class StakeholderCountResponse(BaseModel):
    stakeholder: str
    count: int


class DailyCountResponse(BaseModel):
    day: date
    count: int