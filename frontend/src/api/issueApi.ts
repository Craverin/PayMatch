import { request } from "./httpClient"
import type { Currency } from "./currency"

export type IssueStatus = "open" | "resolved" | "ignored"
export type IssueUpdateStatus = "open" | "ignored"

export interface MissingOrderReferenceDetails {
  payment_id: string
}

export interface OrderNotFoundDetails {
  payment_id: string
  order_id: string
}

export interface MultipleSuccessfulPaymentsDetails {
  order_id: string
  payment_ids: string[]
}

export interface PaymentForCancelledOrderDetails {
  order_id: string
  payment_id: string
}

export interface CurrencyMismatchDetails {
  order_currency: Currency
  payment_currency: Currency
}

export interface AmountMismatchDetails {
  currency: Currency
  order_amount_minor: number
  payment_amount_received_minor: number
  difference_minor: number
}

export interface OrderNotMarkedPaidDetails {
  order_id: string
  payment_id: string
}

export interface PaidOrderWithoutSuccessfulPaymentDetails {
  order_id: string
  payment_statuses: Record<string, string>
}

export interface MissingOrderReferenceIssue {
  type: "MISSING_ORDER_REFERENCE"
  details: MissingOrderReferenceDetails
}

export interface OrderNotFoundIssue {
  type: "ORDER_NOT_FOUND"
  details: OrderNotFoundDetails
}

export interface MultipleSuccessfulPaymentsIssue {
  type: "MULTIPLE_SUCCESSFUL_PAYMENTS"
  details: MultipleSuccessfulPaymentsDetails
}

export interface PaymentForCancelledOrderIssue {
  type: "PAYMENT_FOR_CANCELLED_ORDER"
  details: PaymentForCancelledOrderDetails
}

export interface CurrencyMismatchIssue {
  type: "CURRENCY_MISMATCH"
  details: CurrencyMismatchDetails
}

export interface AmountMismatchIssue {
  type: "AMOUNT_MISMATCH"
  details: AmountMismatchDetails
}

export interface OrderNotMarkedPaidIssue {
  type: "ORDER_NOT_MARKED_PAID"
  details: OrderNotMarkedPaidDetails
}

export interface PaidOrderWithoutSuccessfulPaymentIssue {
  type: "PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT"
  details: PaidOrderWithoutSuccessfulPaymentDetails
}

export type ConcreteIssue =
  | MissingOrderReferenceIssue
  | OrderNotFoundIssue
  | MultipleSuccessfulPaymentsIssue
  | PaymentForCancelledOrderIssue
  | CurrencyMismatchIssue
  | AmountMismatchIssue
  | OrderNotMarkedPaidIssue
  | PaidOrderWithoutSuccessfulPaymentIssue

export type IssueType = ConcreteIssue["type"]

export interface IssueResponse {
  id: number
  order_id: number | null
  payment_id: number | null
  status: IssueStatus
  issue: ConcreteIssue
  created_at: string
  updated_at: string
  resolved_at: string | null
}

export interface IssueStatusUpdate {
  status: IssueUpdateStatus
}

export function getIssues(
  statuses?: IssueStatus | IssueStatus[],
  types?: IssueType | IssueType[],
  limit: number = 25,
  offset: number = 0
): Promise<IssueResponse[]> {
  const params: Record<string, string | string[]> = {}

  if (statuses)
    params["status"] = statuses

  if (types)
    params["type"] = types

  params["limit"] = limit.toString()
  params["offset"] = offset.toString()

  return request<IssueResponse[]>("/api/issues", { params })
}

export function getIssue(id: number): Promise<IssueResponse> {
  return request<IssueResponse>(`/api/issues/${id}`)
}

export function updateIssueStatus(
  id: number,
  status: IssueUpdateStatus
): Promise<IssueResponse> {
  const body: IssueStatusUpdate = { status }

  return request<IssueResponse>(`/api/issues/${id}`, {
    method: "PATCH",
    body
  })
}
