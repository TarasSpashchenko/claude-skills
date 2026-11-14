export const FEATURE_FLAGS = {
  NEW_CHECKOUT: 'new-checkout',
  WISHLIST: 'wishlist',
} as const

export type FeatureFlag = (typeof FEATURE_FLAGS)[keyof typeof FEATURE_FLAGS]
