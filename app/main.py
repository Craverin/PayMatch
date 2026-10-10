from fastapi import FastAPI

from app.api import issue, order, payment, sync


app = FastAPI(title="PayMatch")

app.include_router(issue.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
