from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import TypeAdapter

from app.schemas.shop_order import ShopOrder, ShopOrdersPage


app = FastAPI(title="PayMatch Shop")

ORDERS_PATH = Path(__file__).resolve().with_name("orders.json")
orders = TypeAdapter(list[ShopOrder]).validate_json(ORDERS_PATH.read_text(encoding="utf-8"))


@app.get("/api/orders")
def get_orders(limit: Annotated[int, Query(ge=1, le=100)], cursor: str | None = None) -> ShopOrdersPage:
    start_index = 0

    if cursor is not None:
        orders_id = [order.id for order in orders]

        try:
            start_index = orders_id.index(cursor) + 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Unknown cursor")

    page = orders[start_index:start_index + limit]

    next_cursor = page[-1].id if start_index + len(page) < len(orders) else None

    return ShopOrdersPage(
        data=page,
        next_cursor=next_cursor
    )
