import httpx

from app.schemas.stripe_payment import StripePaymentPage, StripePayment


class StripeClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_payments_page(self, starting_after: str | None = None) -> StripePaymentPage:
        params: dict[str, str] = {"limit": "100"}

        if starting_after is not None:
            params["starting_after"] = starting_after

        response = self.client.get("/v1/payment_intents", params=params)

        response.raise_for_status()

        return StripePaymentPage.model_validate_json(response.content)

    def get_payments(self) -> list[StripePayment]:
        starting_after: str | None = None
        payments: list[StripePayment] = []

        while True:
            payments_page = self.get_payments_page(starting_after=starting_after)

            payments.extend(payments_page.data)

            if not payments_page.has_more:
                break

            starting_after = payments_page.data[-1].id

        return payments