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
