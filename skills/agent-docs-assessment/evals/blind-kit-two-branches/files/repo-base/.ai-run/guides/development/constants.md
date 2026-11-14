# Constants

## Where constants live

- Import every constant from the `@/constants` barrel, including `FEATURE_FLAGS`.
- `LIMITS` is in `src/constants/limits.json`.

## Feature flags

- Flags are booleans: `if (FEATURE_FLAGS.WISHLIST) { ... }`.
- Check a flag in a component with `useFeatureFlag`.
