import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def seed_data():
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        
        if len(existing_users) >= 2:
            print(f"Database already seeded with {len(existing_users)} users")
            return
        
        admin_user = User(
            email="admin@example.com",
            full_name="Admin User",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        worker_user = User(
            email="worker@example.com",
            full_name="Worker User",
            role=UserRole.WORKER,
            hashed_password=get_password_hash("worker123"),
            is_active=True
        )
        
        session.add_all([admin_user, worker_user])
        await session.commit()
        
        print("Database seeded successfully:")
        print("  - Admin: admin@example.com / admin123")
        print("  - Worker: worker@example.com / worker123")


if __name__ == "__main__":
    asyncio.run(seed_data())
