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