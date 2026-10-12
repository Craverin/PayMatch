import { request } from "./httpClient"
import type { Currency } from "./currency"

export type OrderStatus = "open" | "cancelled"
export type PaymentStatus = "paid" | "unpaid"

export interface OrderResponse {
  id: number
  external_id: string
  amount_minor: number
  currency: Currency
  order_status: OrderStatus
  payment_status: PaymentStatus
  external_created_at: string
  external_updated_at: string
  last_sync_run_id: number
}

export function getOrders(
  orderStatuses?: OrderStatus | OrderStatus[],
  paymentStatuses?: PaymentStatus | PaymentStatus[],
  currencies?: Currency | Currency[],
  limit: number = 25,
  offset: number = 0
): Promise<OrderResponse[]> {
  const params: Record<string, string | string[]> = {}

  if (orderStatuses)
    params["order_status"] = orderStatuses

  if (paymentStatuses)
    params["payment_status"] = paymentStatuses

  if (currencies)
    params["currency"] = currencies

  params["limit"] = limit.toString()
  params["offset"] = offset.toString()

  return request<OrderResponse[]>("/api/orders", { params })
}

export function getOrder(id: number): Promise<OrderResponse> {
  return request<OrderResponse>(`/api/orders/${id}`)
}
