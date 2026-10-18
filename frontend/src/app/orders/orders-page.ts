import { Component, computed, inject, signal } from '@angular/core'
import { DatePipe } from '@angular/common'
import { ActivatedRoute, Router, RouterLink } from '@angular/router'
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { getOrder, getOrders } from '../../api/orderApi'
import type { OrderResponse, OrderStatus, PaymentStatus } from '../../api/orderApi'
import type { Currency } from '../../api/currency'
import { DetailPanel } from '../shared/detail-panel'
import { Icon } from '../shared/icon'
import { Pagination } from '../shared/pagination'
import { StatusBadge } from '../shared/status-badge'
import { PAGE_SIZE, currencies, formatMoney, formatChoice, formatId, formatOffset } from '../shared/format'
import { RequestState } from '../shared/request-state'

@Component({
  selector: 'app-orders-page',
  imports: [DatePipe, RouterLink, DetailPanel, Icon, Pagination, StatusBadge],
  templateUrl: './orders-page.html'
})
export class OrdersPage {
  private readonly route = inject(ActivatedRoute)
  private readonly router = inject(Router)

  readonly list = new RequestState<OrderResponse[]>()
  readonly detail = new RequestState<OrderResponse>()

  readonly orderStatus = signal<OrderStatus | ''>('')
  readonly paymentStatus = signal<PaymentStatus | ''>('')
  readonly currency = signal<Currency | ''>('')
  readonly offset = signal(0)
  readonly selectedId = signal<number | null>(null)

  readonly rows = computed(() => (this.list.data() ?? []).slice(0, PAGE_SIZE))

  readonly hasNext = computed(() => (this.list.data()?.length ?? 0) > PAGE_SIZE)

  readonly currencies = currencies
  readonly money = formatMoney

  private listKey = ''

  constructor() {
    this.route.queryParamMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.orderStatus.set(formatChoice(params.get('order_status'), ['open', 'cancelled']))
      this.paymentStatus.set(formatChoice(params.get('payment_status'), ['paid', 'unpaid']))
      this.currency.set(formatChoice(params.get('currency'), currencies))
      this.offset.set(formatOffset(params.get('offset')))

      const key = `${this.orderStatus()}/${this.paymentStatus()}/${this.currency()}/${this.offset()}`
      if (this.listKey !== key) {
        this.listKey = key
        this.loadList()
      }

      const id = formatId(params.get('id'))
      if (id !== this.selectedId()) {
        this.selectedId.set(id)
        this.detail.clear()

        if (id !== null)
          void this.detail.load(() => getOrder(id))
      }
    })
  }

  loadList(): void {
    void this.list.load(() =>
      getOrders(
        this.orderStatus() || undefined,
        this.paymentStatus() || undefined,
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
      void this.detail.load(() => getOrder(id))
  }

  filter(name: 'order_status' | 'payment_status' | 'currency', value: string): void {
    this.navigate({ [name]: value || null, offset: null, id: null })
  }

  navigate(params: Record<string, string | number | null>): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: params,
      queryParamsHandling: 'merge'
    })
  }
}
