# optimise/benchmark.py
"""Benchmark output parsing, convergence loop, and performance evaluation."""
import re


class BenchmarkError(Exception):
    """Raised on benchmark parsing or evaluation failures."""
    pass


def parse_bench_output(text):
    """Parse benchmark output text into a list of row dicts.

    Each non-blank line must be in format: label=value, label=value, ...
    'user' must be present on every line.

    Returns list of dicts, e.g. [{"user": 0.561, "cpu": 5.372}, ...]
    """
    rows = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        pairs = re.findall(r"(\w+)\s*=\s*([^\s,]+)", line)
        if not pairs:
            raise BenchmarkError(f"Cannot parse benchmark line: {line!r}")
        row = {}
        for label, value in pairs:
            try:
                row[label] = float(value)
            except ValueError:
                raise BenchmarkError(f"Invalid numeric value for {label}: {value!r}")
        if "user" not in row:
            raise BenchmarkError(f"Missing 'user' on benchmark line: {line!r}")
        rows.append(row)

    if not rows:
        raise BenchmarkError("Benchmark produced no output")
    return rows


def update_element_best(best, new_rows):
    """Update element-wise best (minimum) across benchmark rows.

    Args:
        best: current best rows (list of dicts), or None for first run
        new_rows: new benchmark rows (list of dicts)

    Returns new best rows list.
    """
    if best is None:
        # Deep copy on first run
        return [{k: v for k, v in row.items()} for row in new_rows]

    if len(best) != len(new_rows):
        raise BenchmarkError(
            f"Benchmark row count changed: expected {len(best)}, got {len(new_rows)}"
        )

    result = []
    for b, n in zip(best, new_rows):
        row = dict(b)
        for label, value in n.items():
            if label in row:
                row[label] = min(row[label], value)
            else:
                row[label] = value
        result.append(row)
    return result


def sum_user(rows):
    """Sum the 'user' values across all rows."""
    return sum(row["user"] for row in rows)


class ConvergenceState:
    """Tracks benchmark convergence using a tail counter.

    The benchmark has converged when improvement stays below threshold_pct
    for tail_runs consecutive updates.
    """

    def __init__(self, threshold_pct, tail_runs):
        self.threshold_pct = threshold_pct
        self.tail_runs = tail_runs
        self.reference_sum = None
        self.tail_counter = 0

    @property
    def converged(self):
        return self.tail_counter >= self.tail_runs

    def update(self, current_sum):
        """Update with new sum(user) value. Call after each benchmark run."""
        if self.reference_sum is None:
            self.reference_sum = current_sum
            return

        improvement_pct = (self.reference_sum - current_sum) / self.reference_sum * 100
        if improvement_pct >= self.threshold_pct:
            self.reference_sum = current_sum
            self.tail_counter = 0
        else:
            self.tail_counter += 1


def evaluate_success(baseline_rows, result_rows, min_improvement_pct, regression_tradeoff):
    """Evaluate whether a benchmark result is a success.

    Args:
        baseline_rows: element-wise best rows from current-best
        result_rows: element-wise best rows from this benchmark run
        min_improvement_pct: minimum sum(user) improvement to accept
        regression_tradeoff: multiplier for individual regression check

    Returns:
        (success: bool, improvement_pct: float, detail: str)
    """
    baseline_sum = sum_user(baseline_rows)
    result_sum = sum_user(result_rows)
    improvement_pct = (baseline_sum - result_sum) / baseline_sum * 100

    # Gate 1: minimum improvement
    if improvement_pct < min_improvement_pct:
        return False, improvement_pct, (
            f"Below minimum improvement threshold: "
            f"{improvement_pct:.2f}% < {min_improvement_pct}%"
        )

    # Gate 2: individual regression tradeoff
    if regression_tradeoff > 0:
        max_row_regression = 0.0
        for b, r in zip(baseline_rows, result_rows):
            if r["user"] > b["user"]:
                row_regression = (r["user"] - b["user"]) / b["user"] * 100
                max_row_regression = max(max_row_regression, row_regression)

        required = regression_tradeoff * max_row_regression
        if max_row_regression > 0 and improvement_pct < required:
            return False, improvement_pct, (
                f"Individual regression too large: row regressed {max_row_regression:.2f}%, "
                f"need {required:.2f}% sum improvement but only got {improvement_pct:.2f}%"
            )

    return True, improvement_pct, (
        f"Reduced sum(user) from {baseline_sum:.3f}s to {result_sum:.3f}s "
        f"(~{improvement_pct:.1f}% improvement)"
    )
