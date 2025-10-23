import uuid
from pydantic import BaseModel
from datetime import datetime
from app.models.ticket import TicketStatus


class TicketBase(BaseModel):
    title: str
    description: str


class TicketCreate(TicketBase):
    client_full_name: str
    client_email: str
    client_phone: str
    client_address: str | None = None


class TicketAssign(BaseModel):
    assigned_to: uuid.UUID


class TicketUpdateStatus(BaseModel):
    status: TicketStatus


class TicketResponse(TicketBase):
    id: uuid.UUID
    status: TicketStatus
    client_id: uuid.UUID
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class TicketDetailResponse(TicketResponse):
    client: dict
    assigned_user: dict | None

    model_config = {"from_attributes": True}
