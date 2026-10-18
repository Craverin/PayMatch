import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  input,
  output,
  viewChild
} from '@angular/core'
import { Icon } from './icon'

@Component({
  selector: 'app-detail-panel',
  imports: [Icon],
  template: `
    <dialog
      #panel
      class="detail-panel"
      aria-labelledby="detail-title"
      (cancel)="$event.preventDefault(); closed.emit()"
      (click)="closeOnBackdrop($event)"
    >
      <header class="panel-header">
        <div>
          <p class="panel-caption">{{ caption() }}</p>
          <h2 id="detail-title">{{ title() }}</h2>
        </div>

        <button
          class="icon-button"
          type="button"
          aria-label="Close details"
          (click)="closed.emit()"
          autofocus
        >
          <app-icon name="close" />
        </button>
      </header>

      <div class="panel-body">
        <ng-content />
      </div>
    </dialog>
  `
})
export class DetailPanel implements AfterViewInit, OnDestroy {
  readonly title = input.required<string>()
  readonly caption = input('Details')

  readonly closed = output<void>()

  private readonly panel =
    viewChild.required<ElementRef<HTMLDialogElement>>('panel')

  ngAfterViewInit(): void {
    this.panel().nativeElement.showModal()
  }

  ngOnDestroy(): void {
    this.panel().nativeElement.close()
  }

  closeOnBackdrop(event: MouseEvent): void {
    const dialog = this.panel().nativeElement
    const bounds = dialog.getBoundingClientRect()

    if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right))
      this.closed.emit()
  }
}
