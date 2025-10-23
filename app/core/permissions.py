from fastapi import HTTPException, status
from app.models.user import UserRole, User


def check_admin_permission(current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def check_worker_or_admin_permission(current_user: User):
    if current_user.role not in [UserRole.ADMIN, UserRole.WORKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Worker or Admin access required"
        )
