# API

## Overview

Backend calls go through `src/api/client.ts`: `apiGet` for JSON, `apiStream` for streamed bodies.

| Part | What it holds | Start here |
|---|---|---|
| `src/api/client.ts` | request helpers | `src/api/client.ts::apiGet` |

## Calling an endpoint

- `apiGet<T>(url, options)` resolves with the parsed JSON. On a non-2xx status it shows an error toast and rejects with the `Response`.
- Pass `skipErrorToast: true` when the caller shows its own message, and catch the rejection.

## Streaming

- `apiStream(url)` returns a `ReadableStream`; call `getReader()` on it before you read chunks.

## Examples

### Upload a file

Source: `src/api/upload.ts::uploadFile`

```ts
export async function uploadFile(file: File, onProgress?: (percent: number) => void): Promise<UploadResult> {
  if (file.size === 0) {
    throw new Error('Cannot upload an empty file')
  }
  const form = new FormData()
  form.append('file', file)
  onProgress?.(0)
  const response = await fetch('/api/uploads', {
    method: 'POST',
    body: form,
    credentials: 'include',
  })
  if (!response.ok) {
    showErrorToast(response.status)
    throw response
  }
  onProgress?.(100)
  const result = (await response.json()) as UploadResult
  if (!result.id || !result.url) {
    throw new Error('Upload response is missing id or url')
```
