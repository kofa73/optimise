# Instance Targeting — Design Specification

Adds the ability to target optimisation at the least-improved benchmark instance rather than overall sum(user) time. This enables focused improvement on lagging instances while guarding against regressions elsewhere.

**Dependency:** Config refactoring spec (sidecar path, module name in settings, sidecar parsing). Evaluation logic and target computation can land first; prompt enrichment with instance parameters requires config refactoring.

---

## 1. Targeting Modes

A new setting `targeting_mode` selects the optimisation strategy:

- **`overall`** (default): optimise sum(user) across all instances. Current behaviour.
- **`least_improved_instance`**: at each GENERATE step, identify the instance that has improved the least (by %) compared to baseline, and focus idea generation on improving that instance.

In `least_improved_instance` mode, the target is recomputed dynamically at each GENERATE cycle. As instances improve, focus shifts automatically to the next-worst performer.

---

## 2. Settings Changes

### New settings

```
targeting_mode: overall          # "overall" or "least_improved_instance"
max_regression_pct: 3            # guard threshold (see Section 4)
```

`targeting_mode` is a string validated against `{"overall", "least_improved_instance"}`.
`max_regression_pct` is a float, default 3.

### Reinterpreted settings

- **`min_improvement_pct`**: applies to the target — sum(user) in overall mode, the targeted instance in instance mode.
- **`early_abort_pct`**: in instance mode, checks BOTH the targeted instance AND sum(user) against current-best. If either exceeds tolerance, abort. In overall mode, unchanged (checks sum only).

### Removed settings

- **`individual_regression_tradeoff`**: fully removed from all code, docs, config templates, current config, and tests. Replaced by `max_regression_pct`.

**Behavioural change:** The old `individual_regression_tradeoff` was a ratio test — it allowed regressions if the overall improvement was large enough (`improvement_pct >= tradeoff * max_row_regression`). The new `max_regression_pct` is a simple absolute cap — no individual instance (or sum, in instance mode) may regress by more than X%, regardless of how much the target improved. This is a deliberate simplification: a flat cap is easier to reason about and configure.

**Migration:** If an existing `settings.conf` contains `individual_regression_tradeoff`, settings validation must emit an error directing the user to replace it with `max_regression_pct`.

---

## 3. Evaluation Logic

Fully replaces the current `evaluate_success()` with a unified two-check model. The old three-gate logic (min improvement, early abort, regression tradeoff) is replaced by exactly two checks per mode:

| | **target** (must improve by `min_improvement_pct`) | **guard** (must not regress by more than `max_regression_pct`) |
|---|---|---|
| **overall mode** | sum(user) | any individual instance |
| **instance mode** | targeted instance | sum(user) |

The roles of sum and instance swap depending on mode. Same two numbers, same mental model.

**Failure of either check causes rejection.** There is no "tradeoff" mechanism — both checks must pass.

### Early abort (both modes)

- Abort if the targeted measure (sum or instance) exceeds `early_abort_pct` tolerance vs current-best.
- In instance mode, also abort if sum(user) exceeds `early_abort_pct` tolerance.
- `early_abort_pct` cannot be disabled. A negative value (e.g., `-2`) means "tolerate up to 2% worse than current-best on the first run" — this accounts for measurement noise since benchmark runs converge downward via best-of-N.

**Mechanism change for instance mode:** Currently `run_benchmark_loop` receives a single `baseline_user_sum` scalar for early abort. In instance mode, it must additionally receive the targeted instance's baseline time and index, so it can check both the instance row and the sum after each run. The function signature gains optional parameters: `target_instance_index` (int or None) and `target_instance_baseline` (float or None). When both are provided, early abort checks both the targeted row and sum(user). When None (overall mode), behaviour is unchanged.

---

## 4. Target Computation

At each GENERATE step, when `targeting_mode` is `least_improved_instance`:

1. Read `baseline-perf.md` and `current-best-perf.md`.
2. Compare row-by-row: `improvement_pct[i] = (baseline[i].user - current[i].user) / baseline[i].user * 100`.
3. The row with the smallest `improvement_pct` is the target.
4. Record: row index, baseline time, current time, improvement %.

This is a pure function in `benchmark.py`: `find_least_improved_instance(baseline_rows, current_rows) -> dict` returning `{"index": int, "baseline_user": float, "current_user": float, "improvement_pct": float}`.

**Row ordering is stable:** benchmark output order is deterministic (darktable processes module instances in pipeline order, which is fixed by the sidecar). The positional index is the identity — row N in baseline always corresponds to row N in current-best and row N in a new benchmark run. Labels (Section 6) are display-only and do not affect ordering.

**Negative improvement:** the formula can produce negative values when an instance has regressed since baseline. The function correctly picks this as the least improved. This is expected, not an edge case.

In `overall` mode, this step is skipped entirely.

### Self-correcting behaviour

If an optimisation for instance A causes instance B to regress badly, instance B may become the least-improved and get targeted next. This could cause oscillations in theory, but every improvement is committed with full statistics, so the user can stop the process, review commits, and choose a compromise.

---

## 5. Idea Generation Prompt

When `targeting_mode` is `least_improved_instance`, the generation prompt includes additional context:

- The targeted instance's **deserialized parameters** from the sidecar (module name from settings; dependency on config refactoring spec).
- Its baseline time, current-best time, and improvement %.
- The average improvement % across all instances (for contrast).
- Instruction to focus ideas on code paths exercised by these parameters.

In `overall` mode, the generation prompt is unchanged.

The **implementation prompt is unchanged** in both modes — the idea content carries enough targeting context because the LLM writes the idea with the targeting information baked in.

---

## 6. Perf Log Format

The perf log gains an optional labels column. When instance labels are available (multi-names from the sidecar), each row gets a human-readable label:

```markdown
# Individual timings
| label | user | cpu |
| ---- | ---- | ---- |
| bloom | 5.727 | 61.097 |
| simulate line drawing | 10.392 | 116.981 |
| ... | ... | ... |
```

`format_perf_log` gains an optional `labels` parameter. When not provided, the format is unchanged (no label column). This ensures backwards compatibility — labelled logs only appear once config refactoring delivers sidecar parsing.

`parse_perf_log` must also be updated to handle the label column: when the first column contains non-numeric strings, treat it as labels and parse the remaining columns as numeric values. Return both the row dicts and the labels list (or None if no labels present).

---

## 7. Data Flow

### `least_improved_instance` mode

```
GENERATE:
  1. Read baseline-perf.md and current-best-perf.md
  2. Compare row-by-row → find least improved instance
  3. Read instance parameters from sidecar (module name from settings)
  4. Build generation prompt with: instance params, timing gap, focus instruction
  5. LLM generates ideas with targeting context baked in

CODE:
  (unchanged — idea content carries the context)

BENCHMARK:
  6. Run benchmark, get rows
  7. Early abort: check BOTH targeted instance AND sum(user) vs current-best
  8. After convergence, evaluate:
     - Target: did targeted instance improve by min_improvement_pct?
     - Guard: did sum(user) regress by more than max_regression_pct?
  9. Accept or reject

SUCCESS:
  10. Update current-best-perf.md (with labels if available)
  11. Next GENERATE cycle recomputes target → may shift to a different instance
```

### `overall` mode

Steps 1–4 are skipped. Step 8 swaps roles: target = sum(user), guard = any individual instance. All other steps identical.

---

## 8. Dependencies

This spec requires the config refactoring spec to deliver:

- **Module name** in settings — needed for XMP filtering and benchmark log matching.
- **Sidecar path** in settings — needed to extract per-instance parameters.
- **Sidecar parsing** — extract and deserialize parameters for instances of the configured module.

The targeting spec can be implemented incrementally:
1. **Phase 1** (no config refactoring needed): evaluation logic (`max_regression_pct` replacing `individual_regression_tradeoff`), target computation, early abort changes.
2. **Phase 2** (requires config refactoring): prompt enrichment with instance parameters, labelled perf logs.
