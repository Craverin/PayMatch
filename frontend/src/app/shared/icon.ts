import { Component, input } from '@angular/core'

const paths = {
  issues: 'M9 3h6l6 6v6l-6 6H9l-6-6V9z M12 8v5 M12 16h.01',
  orders: 'M6 3h12v18l-3-2-3 2-3-2-3 2z M9 8h6 M9 12h6',
  payments: 'M3 5h18v14H3z M3 10h18 M6 15h4',
  sync: 'M20 7v5h-5 M4 17v-5h5 M6 7a7 7 0 0 1 11-2l3 3 M4 16l3 3a7 7 0 0 0 11-2',
  close: 'M6 6l12 12 M18 6 6 18',
  left: 'M14 6l-6 6 6 6',
  right: 'M10 6l6 6-6 6',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  check: 'M5 12l4 4L19 6'
}

@Component({
  selector: 'app-icon',
  template: `
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path [attr.d]="paths[name()]" />
    </svg>
  `,
  styles: `
    :host {
      display: inline-flex;
      width: 18px;
      height: 18px;
      flex: 0 0 18px;
    }
    svg {
      width: 100%;
      height: 100%;
    }
  `
})
export class Icon {
  readonly name = input.required<keyof typeof paths>()

  protected readonly paths = paths
}
