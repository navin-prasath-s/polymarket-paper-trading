from py_clob_client.client import ClobClient

class ClobService:

    @staticmethod
    def get_markets() -> list[dict]:
        host = "https://clob.polymarket.com"
        open_client: ClobClient = ClobClient(host=host)
        start_cursor = "MA=="
        end_cursor = "LTE="

        all_markets = []
        next_cursor = start_cursor
        while next_cursor != end_cursor:
            response = open_client.get_markets(next_cursor=next_cursor)

            markets = response.get("data", [])
            all_markets.extend(markets)

            next_cursor = response.get("next_cursor")

        filtered = [
            m for m in all_markets
            if m.get("enable_order_book") and m.get("accepting_orders")
        ]

        return filtered