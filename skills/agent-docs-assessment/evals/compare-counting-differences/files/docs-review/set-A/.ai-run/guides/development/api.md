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
