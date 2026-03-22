# Normalize Benchmark Weights Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Equalize benchmark preset weights by adjusting XMP iteration counts so each preset runs ~10s, and recycle near-miss ideas for retry.

**Architecture:** Modify the XMP test data file's iteration counts (first int32 in each diffuse params blob), archive old perf-logs, and move eligible failed ideas back to todo.

**Spec:** `docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md`

---

### Task 1: Archive old perf-logs

**Files:**
- Rename: `perf-logs/` → `perf-logs.old_method/`

- [ ] **Step 1: Rename perf-logs directory**

```bash
git mv perf-logs perf-logs.old_method
```

- [ ] **Step 2: Commit**

```bash
git add perf-logs.old_method
git commit -m "archive old perf-logs before benchmark rebalancing

Rename perf-logs/ to perf-logs.old_method/ to preserve historical
data measured under the old unequal-weight scheme.
See docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md"
```

---

### Task 2: Update XMP iteration counts

**Files:**
- Modify: `test-data/DSC_9034.NEF.xmp`

The iteration count is the first little-endian int32 (first 8 hex chars) in each `darktable:params` attribute. The preset name is in the corresponding `darktable:multi_name` attribute.

Mapping of preset name → new iteration count → new hex prefix:

| multi_name | New iter | Hex (LE int32) |
|------------|----------|----------------|
| `_builtin_artistic effects \| bloom` | 10 | `0a000000` |
| `_builtin_artistic effects \| simulate line drawing` | 11 | `0b000000` |
| `_builtin_artistic effects \| simulate watercolor` | 10 | `0a000000` |
| `_builtin_dehaze \| extra contrast` | 9 | `09000000` |
| `_builtin_dehaze \| default` | 9 | `09000000` |
| `_builtin_denoise \| coarse` | 21 | `15000000` |
| `_builtin_denoise \| fine` | 34 | `22000000` |
| `_builtin_denoise \| medium` | 26 | `1a000000` |
| `_builtin_inpaint highlights` | 33 | `21000000` |
| `_builtin_lens deblur \| hard` | 17 | `11000000` |
| `_builtin_lens deblur \| medium` | 20 | `14000000` |
| `_builtin_lens deblur \| soft` | 19 | `13000000` |
| `_builtin_local contrast \| fast` | 6 | `06000000` |
| `_builtin_local contrast \| fine` | 9 | `09000000` |
| `_builtin_local contrast \| normal` | 8 | `08000000` |
| `_builtin_sharpen demosaicing \| AA filter` | 11 | `0b000000` |
| `_builtin_sharpen demosaicing \| no AA filter` | 14 | `0e000000` |
| `_builtin_sharpness \| fast` | 7 | `07000000` |
| `_builtin_sharpness \| normal` | 17 | `11000000` |
| `_builtin_sharpness \| strong` | 20 | `14000000` |
| `_builtin_surface blur` | 10 | `0a000000` |

- [ ] **Step 1: Update each diffuse entry's params**

For each of the 21 `<rdf:li>` entries with `darktable:operation="diffuse"`, find the `darktable:multi_name` attribute, look up the new hex prefix from the table above, and replace the first 8 characters of the `darktable:params` value.

For example, bloom currently has:
```
darktable:params="010000000000000020000000..."
```
Change to:
```
darktable:params="0a0000000000000020000000..."
```

Each edit is: replace the first 8 hex chars of the params value, leave the rest unchanged.

- [ ] **Step 2: Verify the XMP is valid**

```bash
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('test-data/DSC_9034.NEF.xmp')
ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'darktable': 'http://darktable.sf.net/'}
diffuse_count = 0
for li in tree.iter('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'):
    op = li.get('{http://darktable.sf.net/}operation')
    if op == 'diffuse':
        diffuse_count += 1
        name = li.get('{http://darktable.sf.net/}multi_name')
        params = li.get('{http://darktable.sf.net/}params')
        iters = int.from_bytes(bytes.fromhex(params[:8]), 'little')
        print(f'{iters:3d}  {name}')
print(f'\nTotal diffuse entries: {diffuse_count}')
"
```

Expected: 21 diffuse entries with the new iteration counts matching the table above.

- [ ] **Step 3: Commit**

```bash
git add test-data/DSC_9034.NEF.xmp
git commit -m "normalize benchmark preset iteration counts to ~10s each

Adjust XMP iteration counts so all 21 diffuse presets run for
approximately 10 seconds, giving each equal weight in sum(user).
Total expected benchmark time: ~209s.
See docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md"
```

---

### Task 3: Move eligible failed ideas back to todo

**Files:**
- Move from `ideas/done/` to `ideas/todo/`:
  1. `013-swap-sums-angle-loop-order.md`
  2. `0222.093-03-19-23-53-53-eliminate-center-pixel-stack-arrays.md`
  3. `002-2026-03-22-17-19-29-skip-negative-clamping-in-decomposition.md`
  4. `005-2026-03-22-07-18-51-unroll-c2-exp-loop.md`
  5. `2026-03-20-22-52-14-inline-isotropic-convolutions.md`

- [ ] **Step 1: Strip outcome and old timing data from each file**

For each of the 5 files, remove:
- The line starting with `outcome:`
- Everything from `# Individual timings` to the end of the file (the three markdown tables)

Keep only the title line and the description paragraph.

- [ ] **Step 2: Move files to todo**

```bash
git mv ideas/done/013-swap-sums-angle-loop-order.md ideas/todo/
git mv ideas/done/0222.093-03-19-23-53-53-eliminate-center-pixel-stack-arrays.md ideas/todo/
git mv ideas/done/002-2026-03-22-17-19-29-skip-negative-clamping-in-decomposition.md ideas/todo/
git mv ideas/done/005-2026-03-22-07-18-51-unroll-c2-exp-loop.md ideas/todo/
git mv ideas/done/2026-03-20-22-52-14-inline-isotropic-convolutions.md ideas/todo/
```

- [ ] **Step 3: Commit**

```bash
git add ideas/done/ ideas/todo/
git commit -m "recycle 5 near-miss ideas for retry with balanced weights

These ideas showed +0.1% to +0.5% overall improvement but didn't
reach the 1% threshold under the old unequal weighting. With
normalized preset weights they may now clear the acceptance gate."
```

---

### Task 4: Create fresh perf-logs and commit spec

**Files:**
- Create: `perf-logs/.gitkeep`
- Add: `docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md`

- [ ] **Step 1: Create empty perf-logs directory**

```bash
mkdir -p perf-logs
touch perf-logs/.gitkeep
```

- [ ] **Step 2: Commit everything**

```bash
git add perf-logs/.gitkeep docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md
git commit -m "add fresh perf-logs dir and benchmark normalization spec

The next optimiser run will detect the empty perf-logs/ and
re-measure the baseline from the current optimised code."
```
