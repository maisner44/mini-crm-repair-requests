from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.database import get_db
from app.models.client import Client
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter()


@router.post("/repair-requests", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_repair_request(
    ticket_data: TicketCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Client).where(Client.email == ticket_data.client_email)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        client = Client(
            full_name=ticket_data.client_full_name,
            email=ticket_data.client_email,
            phone=ticket_data.client_phone,
            address=ticket_data.client_address
        )
        db.add(client)
        await db.flush()
    
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        client_id=client.id
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    return ticket
