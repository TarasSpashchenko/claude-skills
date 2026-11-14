import { useSnapshot } from 'valtio'
import type { FeatureFlag } from '@/constants/featureFlags'
import { flagsStore } from '@/store/flags'

export function useFeatureFlag(flag: FeatureFlag): boolean {
  const { enabled } = useSnapshot(flagsStore)
  return enabled.includes(flag)
}
