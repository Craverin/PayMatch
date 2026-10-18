import type { Currency } from '../../api/currency'

export const PAGE_SIZE = 25
export const currencies = ['EUR', 'USD'] as const

export function formatChoice<T extends string>(value: string | null, options: readonly T[]): T | '' {
  return options.includes(value as T) ? (value as T) : ''
}

export function formatMoney(amountMinor: number, currency: Currency): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amountMinor / 100)
}

export function formatId(value: string | null): number | null {
  const id = Number(value)

  return Number.isSafeInteger(id) && id > 0 ? id : null
}

export function formatOffset(value: string | null): number {
  const offset = Number(value)

  return Number.isSafeInteger(offset) && offset >= 0 ? offset : 0
}
