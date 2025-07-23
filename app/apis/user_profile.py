from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_async_session
from app.core.user_manager import current_active_user
from app.models.user import User
from app.models.user_profile import UserProfile, UserProfileCreate


router = APIRouter(prefix="/user_profile",
                   tags=["user_profile"])


@router.post("/",
            status_code=status.HTTP_201_CREATED,
            description="Create a user profile.")
async def create_user_profile(
        user_profile: UserProfileCreate,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
) -> dict:
    new_profile = UserProfile(
        user_id=user.id,
        name=user_profile.name,
        user_name=user_profile.user_name,
    )
    try:
        db.add(new_profile)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user profile: {e}"
        )
    return {
        "status": "success",
        "message": "User profile created successfully"
    }