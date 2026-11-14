import { showErrorToast } from '@/utils/toast'

export interface RequestOptions {
  signal?: AbortSignal
  skipErrorToast?: boolean
}

export async function apiGet<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(url, { signal: options.signal, credentials: 'include' })
  if (!response.ok) {
    if (!options.skipErrorToast) showErrorToast(response.status)
    throw response
  }
  return (await response.json()) as T
}

export async function apiStream(url: string): Promise<ReadableStreamDefaultReader<Uint8Array>> {
  const response = await fetch(url, { credentials: 'include' })
  if (!response.ok || !response.body) {
    showErrorToast(response.status)
    throw response
  }
  const reader = response.body.getReader()
  return reader
}
