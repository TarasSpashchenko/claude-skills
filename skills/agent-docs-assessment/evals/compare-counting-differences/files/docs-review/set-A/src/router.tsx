import { createBrowserRouter } from 'react-router'
import { ROUTES } from '@/constants'
import { CartPage } from '@/pages/CartPage'
import { HomePage } from '@/pages/HomePage'
import { ProductPage } from '@/pages/ProductPage'

export const router = createBrowserRouter([
  { path: ROUTES.HOME, element: <HomePage /> },
  { path: ROUTES.CART, element: <CartPage /> },
  { path: ROUTES.PRODUCT, element: <ProductPage /> },
])
