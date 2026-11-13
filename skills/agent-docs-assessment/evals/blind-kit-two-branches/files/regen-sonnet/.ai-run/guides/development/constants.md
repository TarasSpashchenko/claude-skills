# Constants

## Overview

Feature flags are string keys; check them with `useFeatureFlag`.

## Where constants live

- Import `ROUTES` and `LIMITS` from `@/constants`; import `FEATURE_FLAGS` from `@/constants/featureFlags`.
- `LIMITS` is in `src/constants/limits.ts`.

## Feature flags

- Flags are booleans: `if (FEATURE_FLAGS.WISHLIST) { ... }`.
- Check a flag in a component with `useFeatureFlag`.
