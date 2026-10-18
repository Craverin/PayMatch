import { Component, computed, input } from '@angular/core'

const labels: Record<string, string> = {
  open: 'Open',
  resolved: 'Resolved',
  ignored: 'Ignored',
  paid: 'Paid',
  unpaid: 'Unpaid',
  cancelled: 'Cancelled',
  canceled: 'Canceled',
  running: 'Running',
  succeeded: 'Succeeded',
  failed: 'Failed',
  processing: 'Processing',
  requires_payment_method: 'Awaiting payment method',
  requires_confirmation: 'Awaiting confirmation',
  requires_action: 'Action required',
  requires_capture: 'Awaiting capture'
}

@Component({
  selector: 'app-status-badge',
  template: `
    <span class="badge" [attr.data-tone]="tone()">
      <span class="status-dot"></span>
      {{ label() }}
    </span>
  `
})
export class StatusBadge {
  readonly status = input.required<string>()

  readonly label = computed(() => labels[this.status()])

  readonly tone = computed(() => {
    const status = this.status()

    if (['paid', 'resolved', 'succeeded'].includes(status))
      return 'green'

    if (status === 'failed')
      return 'red'

    if (['open', 'running', 'processing'].includes(status))
      return 'blue'

    if (status === 'requires_action')
      return 'attention'

    return 'neutral'
  })
}
