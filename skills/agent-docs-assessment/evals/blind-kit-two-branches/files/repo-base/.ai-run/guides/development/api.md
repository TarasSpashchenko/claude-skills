# API

> Backend calls go through `src/api/client.ts`.

## Calling an endpoint

- `apiGet<T>(url)` never throws: it returns `{ data, error }`, so check `error` before you use `data`.
- Errors show a toast automatically.

## Streaming

- `apiStream(url)` returns a reader; read chunks with `reader.read()`.
