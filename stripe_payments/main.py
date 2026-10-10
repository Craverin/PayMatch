import json
from pathlib import Path

import httpx


PAYMENTS_PATH = Path(__file__).resolve().with_name("payments.json")


def create_payments(client: httpx.Client) -> None:
    payment_requests = json.loads(PAYMENTS_PATH.read_text(encoding="utf-8"))

    for payment_request in payment_requests:
        response = client.post(
            "/v1/payment_intents",
            data=payment_request["data"],
            headers={"Idempotency-Key": payment_request["idempotency_key"]}
        )
        response.raise_for_status()

        payment = response.json()
        print(f"{payment_request['name']}: {payment['id']} ({payment['status']})")


def main() -> None:
    from app.config import HTTP_REQUEST_TIMEOUT, STRIPE_BASE_URL, STRIPE_API_KEY

    with httpx.Client(
        base_url=STRIPE_BASE_URL,
        auth=(STRIPE_API_KEY, ""),
        timeout=HTTP_REQUEST_TIMEOUT
    ) as client:
        create_payments(client)


if __name__ == "__main__":
    main()
