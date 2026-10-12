type HttpMethod = "GET" | "POST" | "PATCH"

interface RequestOptions {
  method?: HttpMethod
  params?: Record<string, string | string[]>
  body?: unknown
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", params = null, body = null } = options
  const headers: Record<string, string> = {}

  if (body !== null)
    headers["Content-Type"] = "application/json"

  const url = new URL(path, window.location.origin)

  if (params !== null) {
    Object.entries(params).forEach(([arg, value]) => {
      if (Array.isArray(value))
        value.forEach((value) => url.searchParams.append(arg, value))

      else if (typeof value === "string")
        url.searchParams.append(arg, value)
    })
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body !== null ? JSON.stringify(body) : undefined
  })

  if (!response.ok) {
    const error: unknown = await response.json().catch(() => null)

    let errorMessage = `Request failed: ${response.status} ${response.statusText}`

    if (
      error != null &&
      typeof error === "object" &&
      "detail" in error
    ) {
      if (typeof error.detail === "string")
        errorMessage = error.detail

      else if (Array.isArray(error.detail)) {
        const messages = error.detail
          .filter(item => item !== null && typeof item === "object" && typeof item.msg === "string")
          .map(item => item.msg)

        if (messages.length > 0)
          errorMessage = messages.join("; ")
      }
    }

    throw new Error(errorMessage)
  }

  return response.json() as Promise<T>
}
