import { Component, input, output } from '@angular/core'
import { PAGE_SIZE } from './format'
import { Icon } from './icon'

@Component({
  selector: 'app-pagination',
  imports: [Icon],
  template: `
    <footer class="pagination">
      <span aria-live="polite">
        {{
          count()
            ? offset() + 1 + '–' + (offset() + count())
            : '0'
        }} records
      </span>

      <div class="pagination-controls">
        <span>Page {{ page() }}</span>

        <button
          type="button"
          class="icon-button"
          aria-label="Previous page"
          [disabled]="loading() || offset() === 0"
          (click)="changed.emit(previous())"
        >
          <app-icon name="left" />
        </button>

        <button
          type="button"
          class="icon-button"
          aria-label="Next page"
          [disabled]="loading() || !hasNext()"
          (click)="changed.emit(offset() + pageSize)"
        >
          <app-icon name="right" />
        </button>
      </div>
    </footer>
  `
})
export class Pagination {
  readonly offset = input.required<number>()
  readonly count = input.required<number>()
  readonly hasNext = input.required<boolean>()
  readonly loading = input(false)

  readonly changed = output<number>()

  readonly pageSize = PAGE_SIZE

  page(): number {
    return Math.floor(this.offset() / PAGE_SIZE) + 1
  }

  previous(): number {
    return Math.max(0, this.offset() - PAGE_SIZE)
  }
}
