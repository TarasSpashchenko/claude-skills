import { describe, expect, it, vi } from 'vitest'
import { apiGet } from '../client'

describe('apiGet', () => {
  it('rejects with the response on a non-2xx status', async () => {
    const response = new Response(null, { status: 500 })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))
    await expect(apiGet('/x', { skipErrorToast: true })).rejects.toBe(response)
  })
})
