import httpx

from app.schemas.shop_order import ShopOrdersPage, ShopOrder


class ShopClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_orders_page(self, cursor: str | None = None) -> ShopOrdersPage:
        params: dict[str, str | int] = {"limit": 100}

        if cursor is not None:
            params["cursor"] = cursor

        response = self.client.get("/api/orders", params=params)

        response.raise_for_status()

        return ShopOrdersPage.model_validate_json(response.content)

    def get_orders(self) -> list[ShopOrder]:
        cursor = None
        orders: list[ShopOrder] = []

        while True:
            orders_page = self.get_orders_page(cursor=cursor)

            orders.extend(orders_page.data)
            cursor = orders_page.next_cursor

            if cursor is None:
                break

        return orders