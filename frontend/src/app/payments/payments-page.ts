import { Component, computed, inject, signal } from '@angular/core'
import { DatePipe } from '@angular/common'
import { ActivatedRoute, Router, RouterLink } from '@angular/router'
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { getPayment, getPayments } from '../../api/paymentApi'
import type { PaymentResponse, ProviderStatus } from '../../api/paymentApi'
import type { Currency } from '../../api/currency'
import { DetailPanel } from '../shared/detail-panel'
import { Icon } from '../shared/icon'
import { Pagination } from '../shared/pagination'
import { StatusBadge } from '../shared/status-badge'
import { PAGE_SIZE, currencies, formatMoney, formatChoice, formatId, formatOffset } from '../shared/format'
import { RequestState } from '../shared/request-state'

@Component({
  selector: 'app-payments-page',
  imports: [DatePipe, RouterLink, DetailPanel, Icon, Pagination, StatusBadge],
  templateUrl: './payments-page.html'
})
export class PaymentsPage {
  private readonly route = inject(ActivatedRoute)
  private readonly router = inject(Router)

  readonly list = new RequestState<PaymentResponse[]>()
  readonly detail = new RequestState<PaymentResponse>()

  readonly providerStatus = signal<ProviderStatus | ''>('')
  readonly currency = signal<Currency | ''>('')
  readonly orderId = signal('')
  readonly offset = signal(0)
  readonly selectedId = signal<number | null>(null)

  readonly rows = computed(() => (this.list.data() ?? []).slice(0, PAGE_SIZE))

  readonly hasNext = computed(() => (this.list.data()?.length ?? 0) > PAGE_SIZE)

  readonly statusOptions: { value: ProviderStatus; label: string }[] = [
    { value: 'succeeded', label: 'Succeeded' },
    { value: 'processing', label: 'Processing' },
    { value: 'requires_payment_method', label: 'Awaiting payment method' },
    { value: 'requires_confirmation', label: 'Awaiting confirmation' },
    { value: 'requires_action', label: 'Action required' },
    { value: 'requires_capture', label: 'Awaiting capture' },
    { value: 'canceled', label: 'Canceled' }
  ]

  readonly currencies = currencies
  readonly money = formatMoney

  private listKey = ''

  constructor() {
    this.route.queryParamMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.providerStatus.set(
        formatChoice(
          params.get('provider_status'),
          this.statusOptions.map((option) => option.value)
        )
      )

      this.currency.set(formatChoice(params.get('currency'), currencies))
      this.orderId.set(params.get('external_order_id') ?? '')
      this.offset.set(formatOffset(params.get('offset')))

      const key = JSON.stringify([
        this.providerStatus(),
        this.currency(),
        this.orderId(),
        this.offset()
      ])

      if (this.listKey !== key) {
        this.listKey = key
        this.loadList()
      }

      const id = formatId(params.get('id'))
      if (id !== this.selectedId()) {
        this.selectedId.set(id)
        this.detail.clear()

        if (id !== null)
          void this.detail.load(() => getPayment(id))
      }
    })
  }

  loadList(): void {
    void this.list.load(() =>
      getPayments(
        this.orderId() || undefined,
        this.providerStatus() || undefined,
        this.currency() || undefined,
        PAGE_SIZE + 1,
        this.offset()
      )
    )
  }

  refresh(): void {
    this.loadList()

    const id = this.selectedId()

    if (id !== null)
      void this.detail.load(() => getPayment(id))
  }

  filter(name: 'external_order_id' | 'provider_status' | 'currency', value: string): void {
    this.navigate({ [name]: value.trim() || null, offset: null, id: null })
  }

  navigate(params: Record<string, string | number | null>): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: params,
      queryParamsHandling: 'merge'
    })
  }
}
