from decimal import Decimal

class OrderService:

    @staticmethod
    def simulate_buy_transaction(amount: Decimal,
                                    book: list[dict]) -> dict:
        amount_left = Decimal(amount)
        total_shares = Decimal("0")
        total_cost = Decimal("0")
        fills = []

        levels = sorted(book, key=lambda x: Decimal(x['price']))

        for level in levels:
            price = Decimal(level['price'])
            size = Decimal(level['size'])
            possible_cost = price * size

            if possible_cost <= amount_left:
                # Can buy all at this price
                total_shares += size
                total_cost += possible_cost
                fills.append({
                    "fill_price": round(float(price), 2),
                    "fill_shares": round(float(size), 2)
                })
                amount_left -= possible_cost
            else:
                # Can only buy part at this price
                shares_affordable = amount_left / price
                if shares_affordable > 0:
                    total_shares += shares_affordable
                    total_cost += shares_affordable * price
                    fills.append({
                        "fill_price": round(float(price), 2),
                        "fill_shares": round(float(shares_affordable), 2)
                    })
                break

        if total_cost < Decimal(amount):
            return {
                "status": "exceeds_liquidity",
                "max_amount": float(total_cost),
                "max_shares": float(total_shares),
                "fills": fills
            }

        return {
            "status": "filled",
            "shares_filled": float(total_shares),
            "total_cost": float(total_cost),
            "fills": fills
        }






if __name__ == "__main__":
    from app.services.clob_service import ClobService
    from decimal import Decimal

    token_data_full = ClobService.get_book_by_token_id(
        "65225399431947441261973886818995257941140037688423054284478538534712119046738", "BUY")

    res = OrderService().simulate_buy_transaction(Decimal('1000'), token_data_full)
    print(res)