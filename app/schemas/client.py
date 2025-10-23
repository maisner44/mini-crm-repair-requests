import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ClientBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    address: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
