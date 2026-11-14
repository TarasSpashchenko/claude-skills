import { proxy } from 'valtio'
import type { FeatureFlag } from '@/constants/featureFlags'

export const flagsStore = proxy({ enabled: [] as FeatureFlag[] })
