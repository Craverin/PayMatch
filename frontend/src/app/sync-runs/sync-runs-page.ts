import { Component, DestroyRef, computed, inject, signal } from '@angular/core'
import { DatePipe } from '@angular/common'
import { ActivatedRoute, Router, RouterLink } from '@angular/router'
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { createSyncRun, getSyncRun, getSyncRuns } from '../../api/syncRunApi'
import type { SyncRunResponse, SyncRunStatus } from '../../api/syncRunApi'
import { DetailPanel } from '../shared/detail-panel'
import { Icon } from '../shared/icon'
import { Pagination } from '../shared/pagination'
import { StatusBadge } from '../shared/status-badge'
import { PAGE_SIZE, formatChoice, formatId, formatOffset } from '../shared/format'
import { RequestState, formatRequestError } from '../shared/request-state'

@Component({
  selector: 'app-sync-runs-page',
  imports: [DatePipe, RouterLink, DetailPanel, Icon, Pagination, StatusBadge],
  templateUrl: './sync-runs-page.html'
})
export class SyncRunsPage {
  private readonly route = inject(ActivatedRoute)
  private readonly router = inject(Router)
  private readonly destroyRef = inject(DestroyRef)

  readonly list = new RequestState<SyncRunResponse[]>()
  readonly detail = new RequestState<SyncRunResponse>()

  readonly status = signal<SyncRunStatus | ''>('')
  readonly offset = signal(0)
  readonly selectedId = signal<number | null>(null)
  readonly starting = signal(false)
  readonly actionError = signal('')

  readonly rows = computed(() => (this.list.data() ?? []).slice(0, PAGE_SIZE))

  readonly hasNext = computed(() => (this.list.data()?.length ?? 0) > PAGE_SIZE)

  readonly running = computed(
    () =>
      this.list.data()?.some((run) => run.status === 'running') ||
      this.detail.data()?.status === 'running'
  )

  private listKey = ''

  constructor() {
    this.route.queryParamMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.status.set(formatChoice(params.get('status'), ['running', 'succeeded', 'failed']))
      this.offset.set(formatOffset(params.get('offset')))

      const key = `${this.status()}/${this.offset()}`
      if (key !== this.listKey) {
        this.listKey = key
        this.loadList()
      }

      const id = formatId(params.get('id'))
      if (id !== this.selectedId()) {
        this.selectedId.set(id)
        this.detail.clear()

        if (id !== null)
          void this.detail.load(() => getSyncRun(id))
      }
    })

    const timer = window.setInterval(() => {
      if (document.visibilityState !== 'visible' || !this.running())
        return

      if (!this.list.loading())
        this.loadList(true)

      const id = this.selectedId()

      if (id !== null && !this.detail.loading())
        void this.detail.load(() => getSyncRun(id), true)
    }, 4000)

    this.destroyRef.onDestroy(() => window.clearInterval(timer))
  }

  loadList(keepData = false): void {
    void this.list.load(
      () => getSyncRuns(this.status() || undefined, PAGE_SIZE + 1, this.offset()),
      keepData
    )
  }

  refresh(): void {
    this.loadList()

    const id = this.selectedId()

    if (id !== null)
      void this.detail.load(() => getSyncRun(id))
  }

  navigate(params: Record<string, string | number | null>): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: params,
      queryParamsHandling: 'merge'
    })
  }

  async start(): Promise<void> {
    if (this.starting() || this.running())
      return

    this.starting.set(true)
    this.actionError.set('')

    try {
      const run = await createSyncRun()

      if (this.destroyRef.destroyed)
        return

      this.loadList()
      this.navigate({ id: run.id })
    } catch (error) {
      this.actionError.set(formatRequestError(error))
    } finally {
      this.starting.set(false)
    }
  }
}
