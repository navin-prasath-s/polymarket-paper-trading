from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.session import get_async_session
from app.core.user_manager import current_active_user
from app.models.user import User
from app.models.order import Order, OrderSide, OrderType, OrderStatus, OrderBuyCreate, OrderSellCreate
from app.models.user_profile import UserProfile, UserProfileRead
from app.services.clob_service import ClobService
from app.services.order_service import OrderService


router = APIRouter(prefix="/order",
                   tags=["order"])

@router.post("/buy",
                status_code=status.HTTP_201_CREATED,
                description="Create a new buy order.")
async def create_buy_order(
        order: OrderBuyCreate,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
) -> dict:

    # 1. Fetch the user profile
    statement = select(UserProfile).where(UserProfile.user_id == user.id)
    result = await db.execute(statement)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    # 2. Check if the user has sufficient balance
    if profile.balance < order.amount_usdc:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Your balance is {profile.balance}, but order requires {order.amount_usdc}."
        )

    #3. Simulate the order
    asks_book = ClobService.get_book_by_token_id(order.token, side="BUY")
    result = OrderService().simulate_buy_transaction(
        amount=order.amount_usdc,
        book=asks_book,
    )

    # 4. If exceeds liquidity
    if result.get("status") == "exceeds_liquidity":
        raise HTTPException(
            status_code=400,
            detail=f"Order exceeds liquidity. "
                   f"Max amount you can buy is {result['max_amount']} USDC and Max shares is {result['max_shares']}."
        )



    return {}

# @router.post("/buy",
#                 status_code=status.HTTP_201_CREATED,
#                 description="Create a new buy order.")
# async def create_buy_order(
#         order: OrderBuyCreate,
#         db: AsyncSession = Depends(get_async_session),
#         user: User = Depends(current_active_user),
# ) -> dict:
#
#     # 1. Fetch the user profile
#     statement = select(UserProfile).where(UserProfile.user_id == user.id)
#     result = await db.execute(statement)
#     profile = result.scalar_one_or_none()
#
#     if not profile:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User profile not found"
#         )
#
#     # 2. Check if the user has sufficient balance
#     if profile.balance < order.amount_usdc:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Insufficient funds. Your balance is {profile.balance}, but order requires {order.amount_usdc}."
#         )
#
#     # 3. Simulate the order
#     if order.side == OrderSide.BUY:
#         asks_book = ClobService.get_book_by_token_id(order.token, side="BUY")
#         result = OrderService().simulate_market_transaction(
#             amount=order.amount_usdc,
#             book=asks_book,
#             side="BUY",
#         )
#     elif order.side == OrderSide.SELL:
#         bids_book = ClobService.get_book_by_token_id(order.token, side="SELL")
#         result = OrderService().simulate_market_transaction(
#             amount=order.amount_usdc,
#             book=bids_book,
#             side="SELL",
#         )
#
#     # 4. If exceeds liquidity
#     if result.get("status") == "exceeds_liquidity":
#         raise HTTPException(
#             status_code=400,
#             detail=f"Order exceeds liquidity. "
#                    f"Max amount you can buy is {result['max_amount']} USDC and Max shares is {result['max_shares']}."
#         )
#
#     return {}
#     # TODO: Validation






