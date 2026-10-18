import { Component, computed, inject, signal } from '@angular/core'
import { DatePipe } from '@angular/common'
import { ActivatedRoute, Router, RouterLink } from '@angular/router'
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { getIssue, getIssues, updateIssueStatus } from '../../api/issueApi'
import type {
  IssueResponse,
  IssueStatus,
  IssueType,
  IssueUpdateStatus
} from '../../api/issueApi'
import { DetailPanel } from '../shared/detail-panel'
import { Icon } from '../shared/icon'
import { Pagination } from '../shared/pagination'
import { StatusBadge } from '../shared/status-badge'
import { PAGE_SIZE, formatId, formatOffset } from '../shared/format'
import { RequestState, formatRequestError } from '../shared/request-state'
import { issueFields, issueTypes, orderReference, paymentReference } from './issue-presentation'

@Component({
  selector: 'app-issues-page',
  imports: [DatePipe, RouterLink, DetailPanel, Icon, Pagination, StatusBadge],
  templateUrl: './issues-page.html'
})
export class IssuesPage {
  private readonly route = inject(ActivatedRoute)
  private readonly router = inject(Router)

  readonly list = new RequestState<IssueResponse[]>()
  readonly detail = new RequestState<IssueResponse>()

  readonly status = signal<IssueStatus | 'all'>('open')
  readonly type = signal<IssueType | ''>('')
  readonly offset = signal(0)
  readonly selectedId = signal<number | null>(null)
  readonly saving = signal(false)
  readonly actionError = signal('')

  readonly rows = computed(() =>
    (this.list.data() ?? []).slice(0, PAGE_SIZE)
  )

  readonly hasNext = computed(() => (this.list.data()?.length ?? 0) > PAGE_SIZE)

  readonly fields = computed(() =>
    this.detail.data() ? issueFields(this.detail.data()!.issue) : []
  )

  readonly statusOptions = ['open', 'resolved', 'ignored', 'all'] as const

  readonly typeOptions = Object.entries(issueTypes)
    .map(([value, info]) => ({
      value,
      label: info.title
    }))

  readonly issueTypes = issueTypes
  readonly orderReference = orderReference
  readonly paymentReference = paymentReference

  private listKey = ''

  constructor() {
    this.route.queryParamMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      const status = params.get('status')

      this.status.set(
        this.statusOptions.includes(status as (typeof this.statusOptions)[number])
          ? (status as IssueStatus | 'all')
          : 'open'
      )

      const type = params.get('type')

      this.type.set(Object.hasOwn(issueTypes, type ?? '') ? (type as IssueType) : '')
      this.offset.set(formatOffset(params.get('offset')))

      const key = `${this.status()}/${this.type()}/${this.offset()}`
      if (key !== this.listKey) {
        this.listKey = key
        this.loadList()
      }

      const id = formatId(params.get('id'))
      if (id !== this.selectedId()) {
        this.selectedId.set(id)
        this.actionError.set('')
        this.detail.clear()

        if (id !== null)
          void this.detail.load(() => getIssue(id))
      }
    })
  }

  loadList(): void {
    const status =
      this.status() === 'all'
        ? undefined
        : this.status() as IssueStatus

    void this.list.load(() =>
      getIssues(status, this.type() || undefined, PAGE_SIZE + 1, this.offset())
    )
  }

  refresh(): void {
    this.loadList()

    const id = this.selectedId()

    if (id !== null)
      void this.detail.load(() => getIssue(id))
  }

  setType(type: string): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        type: type || null,
        offset: null,
        id: null
      },
      queryParamsHandling: 'merge'
    })
  }

  setOffset(offset: number): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        offset: offset || null,
        id: null
      },
      queryParamsHandling: 'merge'
    })
  }

  close(): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { id: null },
      queryParamsHandling: 'merge'
    })
  }

  async setStatus(status: IssueUpdateStatus): Promise<void> {
    const id = this.selectedId()

    if (id === null || this.saving())
      return

    this.saving.set(true)
    this.actionError.set('')

    try {
      const issue = await updateIssueStatus(id, status)

      if (this.selectedId() === id)
        this.detail.data.set(issue)

      this.loadList()
    } catch (error) {
      if (this.selectedId() === id)
        this.actionError.set(formatRequestError(error))
    } finally {
      this.saving.set(false)
    }
  }
}
