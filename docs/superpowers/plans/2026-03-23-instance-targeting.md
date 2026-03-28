# Instance Targeting — Implementation Plan (Phase 1)

**Spec:** `docs/superpowers/specs/2026-03-23-instance-targeting-design.md`

Phase 1 covers: evaluation logic (`max_regression_pct` replacing `individual_regression_tradeoff`), target computation, early abort changes, `targeting_mode` setting, and cleanup of all `individual_regression_tradeoff` references.

Phase 2 (prompt enrichment with instance parameters, labelled perf logs) is deferred until the config refactoring spec lands.

---

## Step 1 — Replace `individual_regression_tradeoff` with `max_regression_pct` in settings

### 1a. Tests for settings changes

**File:** `tests/test_settings.py`

Red: add tests, verify they fail. Green: implement in 1b.

```python
# In TestValidateSettings, update _make_valid_settings (line 63):
# Replace "individual_regression_tradeoff": "2" with "max_regression_pct": "3"

# Add new tests:

def test_max_regression_pct_parsed_as_float(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    settings["max_regression_pct"] = "5.5"
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["max_regression_pct"] == 5.5

def test_max_regression_pct_defaults_to_3(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    del settings["max_regression_pct"]
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["max_regression_pct"] == 3

def test_targeting_mode_defaults_to_overall(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["targeting_mode"] == "overall"

def test_targeting_mode_least_improved_valid(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    settings["targeting_mode"] = "least_improved_instance"
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["targeting_mode"] == "least_improved_instance"

def test_targeting_mode_invalid_raises(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    settings["targeting_mode"] = "bogus"
    with pytest.raises(SettingsError, match="targeting_mode"):
        validate_settings(settings, script_repo=str(tmp_path))

def test_old_regression_tradeoff_raises_migration_error(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    settings["individual_regression_tradeoff"] = "2"
    with pytest.raises(SettingsError, match="individual_regression_tradeoff.*max_regression_pct"):
        validate_settings(settings, script_repo=str(tmp_path))
```

### 1b. Implement settings changes

**File:** `optimise/settings.py`

1. In `_FLOAT_KEYS` (line 15-18): replace `"individual_regression_tradeoff"` with `"max_regression_pct"`.

2. In `validate_settings()`, after the early_abort_pct default (line 136-137), add:

```python
# Default max_regression_pct
if "max_regression_pct" not in result:
    result["max_regression_pct"] = 3

# Default targeting_mode and validate
targeting = result.get("targeting_mode", "overall")
if targeting not in ("overall", "least_improved_instance"):
    raise SettingsError(
        f"targeting_mode must be 'overall' or 'least_improved_instance', "
        f"got: {targeting!r}"
    )
result["targeting_mode"] = targeting

# Migration: reject old setting
if "individual_regression_tradeoff" in result:
    raise SettingsError(
        "individual_regression_tradeoff has been removed. "
        "Replace it with max_regression_pct in your settings.conf."
    )
```

3. In `SETTINGS_TEMPLATE` (line 186-189): replace the `individual_regression_tradeoff` block with:

```
# Maximum allowed regression on the guard measure (percent).
# In 'overall' mode: no individual instance may regress more than this.
# In 'least_improved_instance' mode: sum(user) must not regress more than this.
max_regression_pct: 3

# Targeting mode: "overall" or "least_improved_instance".
# overall: optimise sum(user) across all instances.
# least_improved_instance: dynamically target the least-improved instance.
targeting_mode: overall
```

### 1c. Update live settings.conf

**File:** `settings.conf` (line 21)

Replace `individual_regression_tradeoff: 0.5` with `max_regression_pct: 3`.

---

## Step 2 — Replace `evaluate_success` logic

### 2a. Tests for new evaluate_success

**File:** `tests/test_benchmark.py`

Replace `TestEvaluateSuccess` (lines 121-181) entirely. The new signature is:
`evaluate_success(baseline_rows, result_rows, min_improvement_pct, max_regression_pct, targeting_mode="overall", target_instance_index=None)`

```python
class TestEvaluateSuccess:
    # --- overall mode (default) ---

    def test_overall_clear_improvement_passes(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 9.0}, {"user": 9.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert ok
        assert pct == pytest.approx(10.0)

    def test_overall_below_min_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 9.96}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok
        assert "minimum" in detail.lower() or "below" in detail.lower()

    def test_overall_regression_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.5}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok

    def test_overall_instance_regression_exceeds_cap_fails(self):
        """Guard: any instance regressing > max_regression_pct fails."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.5}]  # row 2: 5% regression > 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok
        assert "regress" in detail.lower()

    def test_overall_instance_regression_within_cap_passes(self):
        """Guard: instance regressing <= max_regression_pct is OK."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.2}]  # row 2: 2% regression <= 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert ok

    def test_overall_no_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok

    # --- instance mode ---

    def test_instance_target_improves_enough_passes(self):
        """Target: the targeted instance must improve by min_improvement_pct."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 10.0}, {"user": 9.0}]   # instance 1: 10% improvement
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert ok
        assert pct == pytest.approx(10.0)  # improvement of targeted instance

    def test_instance_target_not_improved_fails(self):
        """Target: targeted instance barely improved -> fail."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 9.96}]  # instance 1: only 0.4%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert not ok

    def test_instance_sum_regression_exceeds_cap_fails(self):
        """Guard: sum(user) must not regress > max_regression_pct."""
        baseline = [{"user": 5.0}, {"user": 5.0}]   # sum=10
        result = [{"user": 8.0}, {"user": 4.0}]     # sum=12 -> sum regressed 20% > 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert not ok
        assert "regress" in detail.lower()

    def test_instance_sum_regression_within_cap_passes(self):
        """Guard: sum(user) regressing <= max_regression_pct is OK."""
        baseline = [{"user": 5.0}, {"user": 5.0}]   # sum=10
        result = [{"user": 5.1}, {"user": 4.0}]     # sum=9.1, sum improved 9%. inst 1 improved 20%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert ok
```

### 2b. Implement new evaluate_success

**File:** `optimise/benchmark.py`

Replace `evaluate_success` (lines 115-156) with:

```python
def evaluate_success(baseline_rows, result_rows, min_improvement_pct, max_regression_pct,
                     targeting_mode="overall", target_instance_index=None):
    """Evaluate whether a benchmark result is a success.

    Two-check model:
      overall mode:  target = sum(user), guard = any individual instance
      instance mode: target = targeted instance, guard = sum(user)

    Args:
        baseline_rows: element-wise best rows from current-best
        result_rows: element-wise best rows from this benchmark run
        min_improvement_pct: minimum improvement on the target measure
        max_regression_pct: maximum allowed regression on the guard measure
        targeting_mode: "overall" or "least_improved_instance"
        target_instance_index: row index of targeted instance (instance mode only)

    Returns:
        (success: bool, improvement_pct: float, detail: str)
        improvement_pct is always relative to the target measure.
    """
    baseline_sum = sum_user(baseline_rows)
    result_sum = sum_user(result_rows)
    sum_improvement_pct = (baseline_sum - result_sum) / baseline_sum * 100

    if targeting_mode == "least_improved_instance" and target_instance_index is not None:
        # Target: the specific instance
        b = baseline_rows[target_instance_index]["user"]
        r = result_rows[target_instance_index]["user"]
        target_improvement_pct = (b - r) / b * 100

        # Check 1 (target): instance must improve enough
        if target_improvement_pct < min_improvement_pct:
            return False, target_improvement_pct, (
                f"Below minimum improvement on targeted instance {target_instance_index}: "
                f"{target_improvement_pct:.2f}% < {min_improvement_pct}%"
            )

        # Check 2 (guard): sum must not regress beyond cap
        if sum_improvement_pct < -max_regression_pct:
            return False, target_improvement_pct, (
                f"Sum(user) regressed beyond cap: "
                f"{-sum_improvement_pct:.2f}% regression > {max_regression_pct}% allowed"
            )

        return True, target_improvement_pct, (
            f"Instance {target_instance_index}: {b:.3f}s -> {r:.3f}s "
            f"(~{target_improvement_pct:.1f}% improvement); "
            f"sum(user): {baseline_sum:.3f}s -> {result_sum:.3f}s"
        )
    else:
        # Overall mode
        # Check 1 (target): sum must improve enough
        if sum_improvement_pct < min_improvement_pct:
            return False, sum_improvement_pct, (
                f"Below minimum improvement threshold: "
                f"{sum_improvement_pct:.2f}% < {min_improvement_pct}%"
            )

        # Check 2 (guard): no individual instance may regress beyond cap
        max_row_regression = 0.0
        worst_row = -1
        for i, (b, r) in enumerate(zip(baseline_rows, result_rows)):
            if r["user"] > b["user"]:
                row_regression = (r["user"] - b["user"]) / b["user"] * 100
                if row_regression > max_row_regression:
                    max_row_regression = row_regression
                    worst_row = i

        if max_row_regression > max_regression_pct:
            return False, sum_improvement_pct, (
                f"Instance {worst_row} regressed {max_row_regression:.2f}% "
                f"(> {max_regression_pct}% cap)"
            )

        return True, sum_improvement_pct, (
            f"Reduced sum(user) from {baseline_sum:.3f}s to {result_sum:.3f}s "
            f"(~{sum_improvement_pct:.1f}% improvement)"
        )
```

---

## Step 3 — Update cli.py to use new evaluate_success signature

### 3a. Test update

**File:** `tests/test_cli.py`

In `_make_build_state` (around line 107-112): replace `"individual_regression_tradeoff": 2` with `"max_regression_pct": 3`.

In `_make_full_build_state` (around line 135-166): replace the parameter name `individual_regression_tradeoff` with `max_regression_pct` everywhere (parameter, default value, dict key).

At line 485 in `TestDoBuildTestBenchmarkPerfTable.test_individual_regression_too_high_has_perf_table`: replace `individual_regression_tradeoff=2` with `max_regression_pct=2`. Also update the test comment at line 470 to describe the new cap logic (e.g., `# max_regression_pct=2: row 2 regressed 38% > 2% cap → fails guard`).

### 3b. Update cli.py call site

**File:** `optimise/cli.py`

At lines 472-476, replace:

```python
ok, improvement_pct, detail = evaluate_success(
    baseline_rows, best,
    s.settings["min_improvement_pct"],
    s.settings["individual_regression_tradeoff"],
)
```

with:

```python
ok, improvement_pct, detail = evaluate_success(
    baseline_rows, best,
    s.settings["min_improvement_pct"],
    s.settings["max_regression_pct"],
    targeting_mode=s.settings.get("targeting_mode", "overall"),
    target_instance_index=s.settings.get("_target_instance_index"),
)
```

Note: `_target_instance_index` is a runtime value set during GENERATE (Step 5), not a user setting. It uses a `_` prefix to signal this.

---

## Step 4 — Add `find_least_improved_instance`

### 4a. Tests

**File:** `tests/test_benchmark.py`

```python
from optimise.benchmark import find_least_improved_instance


class TestFindLeastImprovedInstance:
    def test_finds_least_improved(self):
        baseline = [{"user": 10.0}, {"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 8.0},  {"user": 9.5},  {"user": 7.0}]
        # improvements: 20%, 5%, 30% → least improved = index 1
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 1
        assert result["baseline_user"] == pytest.approx(10.0)
        assert result["current_user"] == pytest.approx(9.5)
        assert result["improvement_pct"] == pytest.approx(5.0)

    def test_negative_improvement_selected(self):
        """A regressed instance has negative improvement and is the worst."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 9.0},  {"user": 11.0}]
        # improvements: 10%, -10% → least improved = index 1
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 1
        assert result["improvement_pct"] == pytest.approx(-10.0)

    def test_all_same_picks_first(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 9.0},  {"user": 9.0}]
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 0  # tied, first wins

    def test_single_row(self):
        baseline = [{"user": 10.0}]
        current  = [{"user": 9.0}]
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 0
        assert result["improvement_pct"] == pytest.approx(10.0)
```

### 4b. Implementation

**File:** `optimise/benchmark.py`

Add after `sum_user` (after line 81):

```python
def find_least_improved_instance(baseline_rows, current_rows):
    """Find the instance that has improved the least since baseline.

    Returns dict with index, baseline_user, current_user, improvement_pct.
    """
    worst_index = 0
    worst_improvement = float("inf")

    for i, (b, c) in enumerate(zip(baseline_rows, current_rows)):
        improvement = (b["user"] - c["user"]) / b["user"] * 100
        if improvement < worst_improvement:
            worst_improvement = improvement
            worst_index = i

    b = baseline_rows[worst_index]
    c = current_rows[worst_index]
    return {
        "index": worst_index,
        "baseline_user": b["user"],
        "current_user": c["user"],
        "improvement_pct": worst_improvement,
    }
```

---

## Step 5 — Wire targeting into the GENERATE → BENCHMARK flow

### 5a. Tests for instance targeting in the main loop

**File:** `tests/test_cli.py`

Add a test that verifies `_target_instance_index` is set in settings when `targeting_mode` is `least_improved_instance`, and that it flows through to `evaluate_success`.

This is an integration-level test. The key assertion is that when `targeting_mode` is `least_improved_instance`, the GENERATE step reads baseline + current-best, calls `find_least_improved_instance`, and stores the result in `settings["_target_instance_index"]`.

```python
# In TestDoCommand or a new class TestInstanceTargeting:

def test_instance_targeting_sets_target_index(self, tmp_path, monkeypatch):
    """In least_improved_instance mode, GENERATE sets _target_instance_index."""
    from optimise.benchmark import format_perf_log

    script = tmp_path / "script"
    script.mkdir()
    _init_git(script)
    for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
        (script / d).mkdir(parents=True, exist_ok=True)

    baseline = [{"user": 10.0}, {"user": 10.0}]
    current = [{"user": 8.0}, {"user": 9.5}]   # instance 1 least improved
    (script / "perf-logs" / "baseline-perf.md").write_text(format_perf_log(baseline))
    (script / "perf-logs" / "current-best-perf.md").write_text(format_perf_log(current))

    settings = {"targeting_mode": "least_improved_instance"}

    from optimise.cli import _compute_target
    _compute_target(str(script), settings)

    assert settings["_target_instance_index"] == 1
    assert settings["_target_instance_baseline"] == pytest.approx(10.0)
```

### 5b. Implement target computation

**File:** `optimise/cli.py`

First, add `find_least_improved_instance` to the import at line 61-63:

```python
from optimise.benchmark import (
    format_perf_log, parse_perf_log, evaluate_success, sum_user,
    find_least_improved_instance, BenchmarkError,
)
```

Then add a helper function near the top of the file (after imports):

```python
def _compute_target(directory, settings):
    """Set targeting runtime state in settings dict.

    For 'least_improved_instance' mode, reads baseline and current-best
    perf logs and identifies the least-improved instance.
    For 'overall' mode, clears any previous targeting state.
    """
    if settings.get("targeting_mode") != "least_improved_instance":
        settings.pop("_target_instance_index", None)
        settings.pop("_target_instance_baseline", None)
        return

    baseline_path = os.path.join(directory, "perf-logs", "baseline-perf.md")
    current_path = os.path.join(directory, "perf-logs", "current-best-perf.md")
    with open(baseline_path) as f:
        baseline_rows = parse_perf_log(f.read())
    with open(current_path) as f:
        current_rows = parse_perf_log(f.read())

    target = find_least_improved_instance(baseline_rows, current_rows)
    settings["_target_instance_index"] = target["index"]
    settings["_target_instance_baseline"] = target["baseline_user"]

    log.info(
        f"[TARGET] Instance {target['index']}: "
        f"{target['baseline_user']:.3f}s → {target['current_user']:.3f}s "
        f"({target['improvement_pct']:+.1f}% improvement, least improved)"
    )
```

Call `_compute_target(directory, settings)` at the start of the GENERATE block (around line 228, before idea generation).

---

## Step 6 — Update early abort for instance mode

### 6a. Tests

**File:** `tests/test_benchmark.py` (or a new `TestRunBenchmarkLoopInstanceMode` section)

The simplest approach: test `run_benchmark_loop` with `target_instance_index` and `target_instance_baseline` set. When the targeted instance exceeds tolerance, early abort fires.

```python
from optimise.runner import run_benchmark_loop

class TestEarlyAbortInstanceMode:
    def test_early_abort_on_instance_regression(self, tmp_path):
        """In instance mode, abort if targeted instance exceeds tolerance."""
        bench = tmp_path / "bench.sh"
        # Instance 0 is fine, instance 1 (targeted) regresses badly
        bench.write_text("#!/bin/sh\necho 'user=9.0'\necho 'user=12.0'\n")
        bench.chmod(0o755)
        with pytest.raises(BenchmarkError, match="early abort"):
            run_benchmark_loop(
                str(bench), cwd=str(tmp_path),
                baseline_user_sum=20.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
                target_instance_index=1,
                target_instance_baseline=10.0,
            )

    def test_early_abort_on_sum_in_instance_mode(self, tmp_path):
        """In instance mode, also abort if sum exceeds tolerance."""
        bench = tmp_path / "bench.sh"
        # Instance 1 (targeted) improved, but sum is way worse
        bench.write_text("#!/bin/sh\necho 'user=19.0'\necho 'user=9.0'\n")
        bench.chmod(0o755)
        with pytest.raises(BenchmarkError, match="early abort"):
            run_benchmark_loop(
                str(bench), cwd=str(tmp_path),
                baseline_user_sum=20.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
                target_instance_index=1,
                target_instance_baseline=10.0,
            )
```

### 6b. Implement early abort changes

**File:** `optimise/runner.py`

Update `run_benchmark_loop` signature (line 128-130) to add optional parameters:

```python
def run_benchmark_loop(bench_cmd, cwd, baseline_user_sum,
                       num_warmup, convergence_threshold_pct,
                       convergence_tail_runs, early_abort_pct,
                       target_instance_index=None,
                       target_instance_baseline=None):
```

Update the early abort block (lines 160-170) to check both sum and instance:

```python
# Early abort on first real run
if run_idx == 1:
    # Check sum(user) — applies in both modes
    sum_threshold = baseline_user_sum * (1 - early_abort_pct / 100)
    sum_exceeded = current_sum > sum_threshold

    # Check targeted instance — only in instance mode
    instance_exceeded = False
    if target_instance_index is not None and target_instance_baseline is not None:
        instance_time = best[target_instance_index]["user"]
        instance_threshold = target_instance_baseline * (1 - early_abort_pct / 100)
        instance_exceeded = instance_time > instance_threshold

    if sum_exceeded or instance_exceeded:
        improvement_pct = (1 - current_sum / baseline_user_sum) * 100
        raise BenchmarkError(
            f"Benchmark early abort: {current_sum:.3f}s vs "
            f"baseline {baseline_user_sum:.3f}s "
            f"({improvement_pct:+.1f}%, need {early_abort_pct}%)",
            rows=best,
        )
```

**File:** `optimise/cli.py`

Update the `run_benchmark_loop` call in `_do_build_test_benchmark` (lines 456-463) to pass instance parameters:

```python
best = run_benchmark_loop(
    s.settings["bench_cmd"], cwd=s.target_repo_path,
    baseline_user_sum=baseline_sum,
    num_warmup=s.settings["num_warmup_iterations"],
    convergence_threshold_pct=s.settings["benchmark_convergence_threshold_pct"],
    convergence_tail_runs=s.settings["benchmark_convergence_tail_runs"],
    early_abort_pct=s.settings["early_abort_pct"],
    target_instance_index=s.settings.get("_target_instance_index"),
    target_instance_baseline=s.settings.get("_target_instance_baseline"),
)
```

---

## Step 7 — Update tests that reference `individual_regression_tradeoff`

All of these are mechanical replacements:

**File:** `tests/test_cli.py`

| Location | Change |
|---|---|
| `_make_build_state` ~line 111 | `"individual_regression_tradeoff": 2` → `"max_regression_pct": 3` |
| `_make_full_build_state` parameter ~line 137 | `individual_regression_tradeoff=2` → `max_regression_pct=3` |
| `_make_full_build_state` dict ~line 166 | `"individual_regression_tradeoff": individual_regression_tradeoff` → `"max_regression_pct": max_regression_pct` |
| `TestDoBuildTestBenchmarkPerfTable` ~line 485 | `individual_regression_tradeoff=2` → `max_regression_pct=2`; update comment at ~line 470 |
| `TestCodingFailureRevertsScope._setup_repos` ~line 725 | `individual_regression_tradeoff: 2` → `max_regression_pct: 3` |
| `TestBaselinePreconditions._setup_repos` ~line 818 | `individual_regression_tradeoff: 2` → `max_regression_pct: 3` |

---

## Step 8 — Update docs that reference `individual_regression_tradeoff`

**File:** `docs/superpowers/specs/2026-03-14-optimiser-design.md`

1. Lines 142-145: replace the `individual_regression_tradeoff` setting block with `max_regression_pct: 3` and updated comment.
2. Lines 383-391: replace the Gate 2 pseudocode with the new max_regression_pct cap logic.

**File:** `docs/superpowers/plans/2026-03-14-optimiser.md`

This is a historical plan document. Update the 4 references:
- Line 219: `"individual_regression_tradeoff": "2"` → `"max_regression_pct": "3"`
- Line 329: `"individual_regression_tradeoff"` → `"max_regression_pct"` in `_FLOAT_KEYS`
- Line 475: `individual_regression_tradeoff: 2` → `max_regression_pct: 3` in template
- Line 3568: `s.settings["individual_regression_tradeoff"]` → `s.settings["max_regression_pct"]`

**File:** `docs/superpowers/specs/2026-03-22-normalize-benchmark-weights-design.md`

- Line 86: `individual_regression_tradeoff: 0.5` → `max_regression_pct: 3`

---

## Step 9 — Run full test suite and verify

```bash
cd /workspace/optimiser && python -m pytest tests/ -v
```

All tests must pass. Grep for any remaining `individual_regression_tradeoff`:

```bash
grep -r "individual_regression_tradeoff" --include='*.py' --include='*.conf' --include='*.md' .
```

The only hits should be in:
- `docs/superpowers/specs/2026-03-23-instance-targeting-design.md` (the spec that describes the removal — this is correct)
- Any git history references (not in working tree)

---

## Execution Order

Steps 1-3 form a single atomic change: settings + evaluation logic + cli wiring. They must be done together because the old `individual_regression_tradeoff` parameter is removed.

Steps 4-6 add instance targeting (can be done incrementally after 1-3).

Steps 7-8 are cleanup that can be done alongside 1-3.

Step 9 is final verification.

**Recommended grouping:**
1. Steps 1 + 2 + 3 + 7 + 8 together (replace regression tradeoff with max_regression_pct everywhere)
2. Steps 4 + 5 + 6 together (add instance targeting)
3. Step 9 (verify)
