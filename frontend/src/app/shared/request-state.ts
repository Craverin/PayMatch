import { signal } from '@angular/core'

export function formatRequestError(error: unknown): string {
  return error instanceof Error ? error.message : 'The request could not be completed.'
}

export class RequestState<T> {
  readonly data = signal<T | null>(null)
  readonly loading = signal(false)
  readonly error = signal('')

  private version = 0

  async load(loader: () => Promise<T>, keepData = false): Promise<void> {
    const version = ++this.version

    this.loading.set(true)
    this.error.set('')

    if (!keepData)
      this.data.set(null)

    try {
      const data = await loader()

      if (version === this.version)
        this.data.set(data)
    } catch (error) {
      if (version === this.version)
        this.error.set(formatRequestError(error))
    } finally {
      if (version === this.version)
        this.loading.set(false)
    }
  }

  clear(): void {
    this.version++

    this.data.set(null)
    this.error.set('')
    this.loading.set(false)
  }
}
