import { request } from "./httpClient"
import type { Currency } from "./currency"

export type ProviderStatus =
  | "requires_payment_method"
  | "requires_confirmation"
  | "requires_action"
  | "processing"
  | "requires_capture"
  | "canceled"
  | "succeeded"

export interface PaymentResponse {
  id: number
  external_id: string
  external_order_id: string | null
  amount_minor: number
  amount_received_minor: number
  currency: Currency
  status: ProviderStatus
  external_created_at: string
  last_changed_at: string
  last_sync_run_id: number
}

export function getPayments(
  externalOrderIds?: string | string[],
  providerStatuses?: ProviderStatus | ProviderStatus[],
  currencies?: Currency | Currency[],
  limit: number = 25,
  offset: number = 0
): Promise<PaymentResponse[]> {
  const params: Record<string, string | string[]> = {}

  if (externalOrderIds)
    params["external_order_id"] = externalOrderIds

  if (providerStatuses)
    params["provider_status"] = providerStatuses

  if (currencies)
    params["currency"] = currencies

  params["limit"] = limit.toString()
  params["offset"] = offset.toString()

  return request<PaymentResponse[]>("/api/payments", { params })
}

export function getPayment(id: number): Promise<PaymentResponse> {
  return request<PaymentResponse>(`/api/payments/${id}`)
}
