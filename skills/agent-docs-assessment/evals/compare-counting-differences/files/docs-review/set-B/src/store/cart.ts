import { proxy } from 'valtio'
import { apiGet } from '@/api/client'

export interface CartItem {
  id: string
  quantity: number
}

export const cartStore = proxy({
  items: [] as CartItem[],
  error: null as string | null,
  async load() {
    try {
      cartStore.items = await apiGet<CartItem[]>('/api/cart', { skipErrorToast: true })
    } catch {
      cartStore.error = 'Could not load the cart'
    }
  },
})
