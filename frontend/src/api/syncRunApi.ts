import { request } from "./httpClient"

export type SyncRunStatus = "running" | "succeeded" | "failed"

export interface SyncRunResponse {
  id: number
  status: SyncRunStatus
  started_at: string
  finished_at: string | null
  orders_imported: number
  payments_imported: number
  error: string | null
}

export interface SyncRunCreatedResponse {
  id: number
  status: "running"
}

export function getSyncRuns(
  statuses?: SyncRunStatus | SyncRunStatus[],
  limit: number = 25,
  offset: number = 0
): Promise<SyncRunResponse[]> {
  const params: Record<string, string | string[]> = {}

  if (statuses)
    params["status"] = statuses

  params["limit"] = limit.toString()
  params["offset"] = offset.toString()

  return request<SyncRunResponse[]>("/api/sync-runs", { params })
}

export function getSyncRun(id: number): Promise<SyncRunResponse> {
  return request<SyncRunResponse>(`/api/sync-runs/${id}`)
}

export function createSyncRun(): Promise<SyncRunCreatedResponse> {
  return request<SyncRunCreatedResponse>("/api/sync-runs", { method: "POST" })
}
