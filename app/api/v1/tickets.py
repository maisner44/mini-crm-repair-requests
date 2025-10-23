from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Annotated
from datetime import datetime
import uuid

from app.database import get_db
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole
from app.schemas.ticket import (
    TicketResponse,
    TicketDetailResponse,
    TicketAssign,
    TicketUpdateStatus
)
from app.api.deps import CurrentUser
from app.core.permissions import check_admin_permission
from app.utils.pagination import paginate, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TicketDetailResponse])
async def list_tickets(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: TicketStatus | None = Query(None),
    search: str | None = Query(None)
):
    query = select(Ticket).options(
        selectinload(Ticket.client),
        selectinload(Ticket.assigned_user)
    )
    
    if current_user.role == UserRole.WORKER:
        query = query.where(Ticket.assigned_to == current_user.id)
    
    if status:
        query = query.where(Ticket.status == status)
    
    if search:
        query = query.where(Ticket.title.ilike(f"%{search}%"))
    
    query = query.order_by(Ticket.created_at.desc())
    
    items, total, total_pages = await paginate(db, query, page, page_size)
    
    formatted_items = []
    for ticket in items:
        ticket_dict = {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "client_id": ticket.client_id,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "completed_at": ticket.completed_at,
            "client": {
                "id": ticket.client.id,
                "full_name": ticket.client.full_name,
                "email": ticket.client.email,
                "phone": ticket.client.phone,
            },
            "assigned_user": {
                "id": ticket.assigned_user.id,
                "full_name": ticket.assigned_user.full_name,
                "email": ticket.assigned_user.email,
            } if ticket.assigned_user else None
        }
        formatted_items.append(ticket_dict)
    
    return PaginatedResponse(
        items=formatted_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Ticket)
        .options(selectinload(Ticket.client), selectinload(Ticket.assigned_user))
        .where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if current_user.role == UserRole.WORKER and ticket.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "client_id": ticket.client_id,
        "assigned_to": ticket.assigned_to,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "completed_at": ticket.completed_at,
        "client": {
            "id": ticket.client.id,
            "full_name": ticket.client.full_name,
            "email": ticket.client.email,
            "phone": ticket.client.phone,
        },
        "assigned_user": {
            "id": ticket.assigned_user.id,
            "full_name": ticket.assigned_user.full_name,
            "email": ticket.assigned_user.email,
        } if ticket.assigned_user else None
    }


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: uuid.UUID,
    assign_data: TicketAssign,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    check_admin_permission(current_user)
    
    worker_result = await db.execute(
        select(User).where(User.id == assign_data.assigned_to)
    )
    worker = worker_result.scalar_one_or_none()
    
    if not worker or worker.role != UserRole.WORKER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker not found"
        )
    
    ticket_result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = ticket_result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket.assigned_to = assign_data.assigned_to
    ticket.status = TicketStatus.ASSIGNED
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: uuid.UUID,
    status_data: TicketUpdateStatus,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if current_user.role == UserRole.WORKER:
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own tickets"
            )
    
    ticket.status = status_data.status
    
    if status_data.status == TicketStatus.DONE:
        ticket.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket
