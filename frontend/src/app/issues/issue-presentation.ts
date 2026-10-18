import type { ConcreteIssue, IssueResponse, IssueType } from '../../api/issueApi'
import { formatMoney } from '../shared/format'

export const issueTypes: Record<IssueType, { title: string; description: string }> = {
  MISSING_ORDER_REFERENCE: {
    title: 'Missing order reference',
    description:
      'The successful payment has no order reference. Check its order_id metadata in Stripe.'
  },

  ORDER_NOT_FOUND: {
    title: 'Order not found',
    description: 'The payment refers to an order that is not present in the imported shop data.'
  },

  MULTIPLE_SUCCESSFUL_PAYMENTS: {
    title: 'Multiple successful payments',
    description:
      'More than one successful payment refers to this order. Review the payments for a possible duplicate.'
  },

  PAYMENT_FOR_CANCELLED_ORDER: {
    title: 'Payment for cancelled order',
    description: 'A successful payment was found for an order that the shop has cancelled.'
  },

  CURRENCY_MISMATCH: {
    title: 'Currency mismatch',
    description:
      'The payment currency differs from the order currency. Amounts in different currencies cannot be compared directly.'
  },

  AMOUNT_MISMATCH: {
    title: 'Amount mismatch',
    description:
      'The amount received by Stripe differs from the order total. The difference is payment received minus order total.'
  },

  ORDER_NOT_MARKED_PAID: {
    title: 'Order not marked paid',
    description: 'A successful payment exists, but the shop still marks the order as unpaid.'
  },

  PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT: {
    title: 'Paid order without payment',
    description:
      'The shop marks this order as paid, but no successful payment was found in the imported Stripe data.'
  }
}

export function issueFields(issue: ConcreteIssue): { label: string; value: string }[] {
  switch (issue.type) {
    case 'MISSING_ORDER_REFERENCE':
      return [{ label: 'Payment reference', value: issue.details.payment_id }]

    case 'ORDER_NOT_FOUND':
    case 'PAYMENT_FOR_CANCELLED_ORDER':
    case 'ORDER_NOT_MARKED_PAID':
      return [
        { label: 'Order reference', value: issue.details.order_id },
        { label: 'Payment reference', value: issue.details.payment_id }
      ]

    case 'MULTIPLE_SUCCESSFUL_PAYMENTS':
      return [
        { label: 'Order reference', value: issue.details.order_id },
        { label: 'Successful payments', value: issue.details.payment_ids.join('\n') }
      ]

    case 'CURRENCY_MISMATCH':
      return [
        { label: 'Order currency', value: issue.details.order_currency },
        { label: 'Payment currency', value: issue.details.payment_currency }
      ]

    case 'AMOUNT_MISMATCH':
      return [
        {
          label: 'Order total',
          value: formatMoney(issue.details.order_amount_minor, issue.details.currency)
        },

        {
          label: 'Payment received',
          value: formatMoney(issue.details.payment_amount_received_minor, issue.details.currency)
        },

        {
          label: 'Difference',
          value:
            (issue.details.difference_minor > 0 ? '+' : '') +
            formatMoney(issue.details.difference_minor, issue.details.currency)
        }
      ]

    case 'PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT':
      return [
        { label: 'Order reference', value: issue.details.order_id },

        ...Object.entries(issue.details.payment_statuses)
          .map(([id, status]) => ({
            label: id,
            value: status.replaceAll('_', ' ')
          })),

        ...(Object.keys(issue.details.payment_statuses).length === 0
          ? [{ label: 'Payments found', value: 'None' }]
          : [])
      ]
  }
}

export function orderReference(issue: IssueResponse): string {
  return 'order_id' in issue.issue.details
    ? issue.issue.details.order_id
    : `Order #${issue.order_id}`
}

export function paymentReference(issue: IssueResponse): string {
  return 'payment_id' in issue.issue.details
    ? issue.issue.details.payment_id
    : `Payment #${issue.payment_id}`
}
