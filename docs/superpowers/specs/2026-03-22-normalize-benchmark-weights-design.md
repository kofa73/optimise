# Normalize Benchmark Preset Weights

**Date:** 2026-03-22
**Status:** Approved

## Problem

The benchmark runs 21 diffuse presets with their built-in iteration counts, producing runtimes from 0.7s to 47s. "Simulate line drawing" (50 iterations, 47s) alone accounts for 27% of the total sum(user). The acceptance criterion requires 1% improvement on sum(user).

This creates two problems:

1. **Heavy preset dominance:** A 3.7% speedup on "simulate line drawing" alone crosses the 1% threshold, even if it's a rarely-used artistic preset.
2. **Fast preset blindness:** The bottom 8 presets (all 1-3 iterations) total 7.7% of weight. A 13% speedup across all of them still doesn't reach 1% overall. Common presets like "sharpen demosaicing" and "sharpness" are effectively invisible to the acceptance gate.

## Solution

Adjust the iteration counts in the XMP test file so each preset runs for approximately 10 seconds, giving each roughly equal weight (~4.8%) in the sum. No changes to the acceptance criteria or benchmark code.

## Target Iteration Counts

Computed from current-best per-iteration timings (`current_time / current_iterations`, rounded to nearest integer targeting ~10s):

| Preset | Current iter | s/iter | New iter | Expected time |
|--------|-------------|--------|----------|---------------|
| bloom | 1 | 0.96 | 10 | 9.6s |
| simulate line drawing | 50 | 0.95 | 11 | 10.4s |
| simulate watercolor | 4 | 0.99 | 10 | 9.9s |
| dehaze extra contrast | 10 | 1.11 | 9 | 10.0s |
| dehaze default | 10 | 1.11 | 9 | 10.0s |
| denoise coarse | 32 | 0.48 | 21 | 10.1s |
| denoise fine | 32 | 0.29 | 34 | 9.9s |
| denoise medium | 32 | 0.39 | 26 | 10.0s |
| inpaint highlights | 32 | 0.30 | 33 | 9.9s |
| lens deblur hard | 24 | 0.58 | 17 | 9.9s |
| lens deblur medium | 16 | 0.49 | 20 | 9.9s |
| lens deblur soft | 8 | 0.52 | 19 | 9.8s |
| local contrast fast | 1 | 1.55 | 6 | 9.3s |
| local contrast fine | 5 | 1.13 | 9 | 10.2s |
| local contrast normal | 10 | 1.23 | 8 | 9.8s |
| sharpen demosaic AA | 1 | 0.92 | 11 | 10.2s |
| sharpen demosaic noAA | 1 | 0.72 | 14 | 10.0s |
| sharpness fast | 1 | 1.37 | 7 | 9.6s |
| sharpness normal | 3 | 0.58 | 17 | 9.9s |
| sharpness strong | 6 | 0.51 | 20 | 10.3s |
| surface blur | 2 | 1.02 | 10 | 10.2s |

Estimated total: ~209s (within the desired 200-250s range).

## XMP Modification

The iteration count is the first little-endian int32 (first 8 hex chars) in each diffuse entry's `darktable:params` blob. For example, bloom's `01000000` = 1 iteration. Each of the 21 diffuse entries in `test-data/DSC_9034.NEF.xmp` gets its first 8 hex chars replaced with the new iteration count.

## Implementation Steps

### Step 1: Archive old perf-logs

Rename `perf-logs/` to `perf-logs.old_method/` and commit. This preserves the historical data under the old weighting scheme.

### Step 2: Update XMP iteration counts

Modify `test-data/DSC_9034.NEF.xmp` — update the first 4 bytes (8 hex chars) of the `darktable:params` attribute for each of the 21 diffuse history entries. The preset names are in `darktable:multi_name` attributes, making each entry identifiable.

### Step 3: Move eligible failed ideas back to todo

Five ideas in `ideas/done/` were marked "target not reached" but showed mild overall improvement (+0.1% to +0.5%). With rebalanced weights, they deserve a retry:

1. `013-swap-sums-angle-loop-order.md` (+0.1%)
2. `0222.093-03-19-23-53-53-eliminate-center-pixel-stack-arrays.md` (+0.1%)
3. `002-2026-03-22-17-19-29-skip-negative-clamping-in-decomposition.md` (+0.2%)
4. `005-2026-03-22-07-18-51-unroll-c2-exp-loop.md` (+0.3%)
5. `2026-03-20-22-52-14-inline-isotropic-convolutions.md` (+0.5%)

Strip the `outcome:` line and individual timings from each before moving, since those stats are from the old weighting.

### Step 4: Create fresh perf-logs

Create an empty `perf-logs/` directory. The next optimiser run will detect the missing baseline and re-measure it from the current optimised code.

### Step 5: Commit

Commit the XMP change, idea moves, and fresh perf-logs directory.

## Acceptance Criteria (unchanged)

- `min_improvement_pct: 1` on sum(user)
- `max_regression_pct: 3`
- `early_abort_pct: -2`

With equal weights, 1% threshold means ~2.1s improvement needed. A 10% speedup on any single preset (~1s) moves the sum by ~0.5%. An optimisation helping 2-3 presets will clear the bar.

## Future Consideration

If after running with normalized weights, single-preset improvements are still being missed, the acceptance criteria can be extended to also accept ideas where: no preset regresses beyond noise, and at least one preset improves by a per-preset threshold. This is a small change to `evaluate_success()` in `optimise/benchmark.py`.

## Documentation

This spec serves as the primary documentation for the weighting change. The commit message for the XMP change should reference this spec.
