from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.session import get_async_session
from app.core.user_manager import current_active_user
from app.models.market_outcome import MarketOutcome
from app.models.order_fill import OrderFill
from app.models.user import User
from app.models.order import Order, OrderSide, OrderType, OrderStatus, OrderBuyCreate, OrderSellCreate
from app.models.user_position import UserPosition
from app.models.user_profile import UserProfile
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

    # 1. Check if market and token exists in market_outcome db
    market_outcome_statement = (
        select(MarketOutcome)
        .options(selectinload(MarketOutcome.market_obj))
        .where(
            MarketOutcome.market == order.market,
            MarketOutcome.token == order.token
        )
    )
    market_outcome_result = await db.execute(market_outcome_statement)
    market_outcome = market_outcome_result.scalar_one_or_none()
    if not market_outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid market/token combination. Market '{order.market}' with token '{order.token}' not found."
        )

    # 2. Check if market is active
    if not market_outcome.market_obj.is_tradable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Market '{order.market}' is not tradable at this time."
        )


    # 3. Fetch the user user_profile
    statement = select(UserProfile).where(UserProfile.user_id == user.id)
    result = await db.execute(statement)
    user_profile = result.scalar_one_or_none()
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User user_profile not found"
        )

    # 4. Check if the user has sufficient balance
    if user_profile.balance < order.amount_usdc:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Your balance is {user_profile.balance}, but order requires {order.amount_usdc}."
        )

    # 5. Simulate the order
    asks_book = ClobService.get_book_by_token_id(order.token, side="BUY")
    result = OrderService().simulate_buy_transaction(
        amount=order.amount_usdc,
        book=asks_book,
    )

    # 6. If exceeds liquidity
    if result.get("status") == "exceeds_liquidity":
        raise HTTPException(
            status_code=400,
            detail=f"Order exceeds liquidity. "
                   f"Max amount you can buy is {result['max_amount']} USDC and Max shares is {result['max_shares']}."
        )

    total_cost = result.get("total_cost")
    total_shares = result.get("shares_filled")
    fills = result.get("fills")

    # 7. Commit to db
    try:
        # 7a. Update user_profile balance
        user_profile.balance -= total_cost

        # 7b. Upsert UserPosition table
        user_position_statement = select(UserPosition).where(
            UserPosition.user_id == user_profile.user_id,
            UserPosition.market == order.market,
            UserPosition.token == order.token
        )
        result = await db.execute(user_position_statement)
        existing_position = result.scalar_one_or_none()

        if existing_position:
            existing_position.shares += total_shares
        else:
            new_position = UserPosition(
                user_id=user_profile.user_id,
                market=order.market,
                token=order.token,
                shares=total_shares
            )
            db.add(new_position)

        # 7c. Create Order
        new_order = Order(
            user_id=user_profile.user_id,
            market=order.market,
            token=order.token,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            amount_usdc=total_cost,
            shares=total_shares,
        )
        db.add(new_order)
        await db.flush()

        # 7d. Create OrderFill
        for fill in fills:
            order_fill = OrderFill(
                order_id=new_order.order_id,
                fill_price=fill['fill_price'],
                fill_shares=fill['fill_shares'],
            )
            db.add(order_fill)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the order: {str(e)}"
        )


    return {
        "order_id": new_order.order_id,
        "status": "success",
        "details": {
            "amount_usdc": total_cost,
            "shares": total_shares,
            "average_price": total_cost / total_shares,
            "fills": len(fills)
        }
    }









