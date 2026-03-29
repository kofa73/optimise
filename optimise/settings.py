"""Settings parsing and validation for the optimiser."""
import os
import re


class SettingsError(Exception):
    """Raised when settings are invalid."""
    pass


# Keys that must have non-empty string values
_REQUIRED_STRING_KEYS = ["target_repo", "branch", "optimisation_target", "instructions", "build_cmd", "bench_cmd"]

# Keys that are converted to float
_FLOAT_KEYS = [
    "min_improvement_pct", "max_regression_pct",
    "benchmark_convergence_threshold_pct", "early_abort_pct",
]

# Keys that are converted to int
_INT_KEYS = [
    "num_warmup_iterations", "benchmark_convergence_tail_runs",
    "max_retries", "max_iterations", "max_consecutive_perf_failures",
    "max_runtime_minutes", "idea_generation_batch_size", "llm_timeout",
    "providers_retry_limit",
]


def parse_settings(path):
    """Parse a settings.conf file into a dict.

    Format: key: value (one per line). # comments and blank lines ignored.
    Raises FileNotFoundError if path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Settings file not found: {path}")
    config = {}
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"(\w[\w-]*):\s*(.*)", line)
            if m:
                key = m.group(1)
                val = m.group(2).strip()
                if key == "disabled_providers":
                    providers = [p.strip() for p in val.split(",") if p.strip()]
                    unknown = [p for p in providers if p not in ("claude", "gemini")]
                    if unknown:
                        raise SettingsError(f"Line {line_num}: Unknown provider(s) in disabled_providers: {', '.join(unknown)}")
                    config[key] = providers
                else:
                    config[key] = val
    return config


def validate_settings(raw, script_repo):
    """Validate raw settings dict and convert numeric types.

    Args:
        raw: dict from parse_settings
        script_repo: absolute path to the script repo root

    Returns:
        dict with validated and type-converted values.

    Raises:
        SettingsError with actionable message on any problem.
    """
    errors = []
    result = dict(raw)

    # Check required string keys exist and are non-empty (except quality_cmd)
    for key in _REQUIRED_STRING_KEYS:
        if key not in result:
            errors.append(f"Missing required setting: {key}")
        elif not result[key]:
            errors.append(f"Setting '{key}' must not be empty")

    if errors:
        raise SettingsError("; ".join(errors))

    # Validate target_repo exists
    if not os.path.isdir(result["target_repo"]):
        raise SettingsError(f"target_repo does not exist: {result['target_repo']}")

    # Parse and validate optimisation_target (comma-separated, files must exist)
    targets = [t.strip() for t in result["optimisation_target"].split(",")]
    targets = [t for t in targets if t]
    for t in targets:
        full_path = os.path.join(result["target_repo"], t)
        if not os.path.isfile(full_path):
            raise SettingsError(
                f"optimisation_target file not found: {t} "
                f"(looked at {full_path})"
            )
    result["optimisation_target"] = targets

    # Validate instructions file exists
    instr_path = result["instructions"]
    if not os.path.isabs(instr_path):
        instr_path = os.path.join(script_repo, instr_path)
    if not os.path.isfile(instr_path):
        raise SettingsError(f"instructions file not found: {result['instructions']}")
    result["instructions"] = instr_path

    # Convert numeric values
    for key in _FLOAT_KEYS:
        if key in result:
            try:
                result[key] = float(result[key])
            except ValueError:
                raise SettingsError(f"Setting '{key}' must be a number, got: {result[key]}")

    for key in _INT_KEYS:
        if key in result:
            try:
                result[key] = int(result[key])
            except ValueError:
                raise SettingsError(f"Setting '{key}' must be an integer, got: {result[key]}")

    # Ensure quality_cmd is present (may be empty)
    if "quality_cmd" not in result:
        result["quality_cmd"] = ""

    # Ensure commit_prefix is present
    if "commit_prefix" not in result:
        result["commit_prefix"] = "perf"

    # Parse commit_scope (comma-separated path prefixes, default: src/)
    raw_scope = result.get("commit_scope", "src/")
    scopes = [s.strip() for s in raw_scope.split(",") if s.strip()]
    result["commit_scope"] = scopes

    # Default early_abort_pct to min_improvement_pct if not provided
    if "early_abort_pct" not in result:
        result["early_abort_pct"] = result.get("min_improvement_pct", 0.5)

    # Default max_regression_pct
    if "max_regression_pct" not in result:
        result["max_regression_pct"] = 3.0

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

    # Default llm_timeout
    if "llm_timeout" not in result:
        result["llm_timeout"] = 3600

    # Default providers_retry_limit
    if "providers_retry_limit" not in result:
        result["providers_retry_limit"] = 0

    return result


# Template for `init` command
SETTINGS_TEMPLATE = """\
# === Target Repository ===
target_repo: <absolute path to the target repository>

# === Branch ===
# Both repos will use this branch. Created from main/master if it doesn't exist.
branch: <branch name, e.g. optimise-diffuse>

# === Files to Optimise ===
# Paths relative to target repo root. Comma-separated for multiple files.
optimisation_target: <list of files; paths relative to target repo root>

# === Instructions ===
# Path to the instructions markdown file, relative to this script repo.
instructions: instructions.md

# === Commands ===
# Build command, run from target repo root.
build_cmd: <command to build the project>

# Quality check command, run from target repo root.
# Leave blank if no quality check is needed.
quality_cmd:

# Benchmark command, run from target repo root.
# Must output lines in format: user=0.123, cpu=0.456, gpu=0.789
# 'user' is mandatory on every line; other labels are informational.
bench_cmd: <command to run performance benchmark>

# === Performance Thresholds ===
# Minimum sum(user) improvement to accept a change (percent).
# Changes below this are treated as noise and reverted.
min_improvement_pct: 0.5

# Minimum improvement on the FIRST benchmark iteration to continue benchmarking (percent).
# If the first run doesn't beat this, the benchmark is aborted early to save time.
# Defaults to min_improvement_pct if not set. Typically set lower.
early_abort_pct: 0.5

# Maximum allowed regression on the guard measure (percent).
# In 'overall' mode: no individual instance may regress more than this.
# In 'least_improved_instance' mode: sum(user) must not regress more than this.
max_regression_pct: 3

# Targeting mode: "overall" or "least_improved_instance".
# overall: optimise sum(user) across all instances.
# least_improved_instance: dynamically target the least-improved instance.
targeting_mode: overall

# === Benchmark Convergence ===
# Number of warmup iterations (output discarded) before real measurement.
num_warmup_iterations: 0

# Improvement below this percentage is considered noise/tail (percent).
benchmark_convergence_threshold_pct: 0.1

# Stop benchmarking if improvement stays below convergence threshold
# for this many consecutive runs.
benchmark_convergence_tail_runs: 5

# === Retry ===
# Max combined build + quality check retries before abandoning an idea.
max_retries: 5

# === Termination ===
# Stop after this many iterations of the main loop.
max_iterations: 50

# Stop after this many consecutive ideas with no performance improvement.
# Only counts performance regressions/no-change, not build/quality failures.
max_consecutive_perf_failures: 5

# Stop after this many minutes of total runtime.
max_runtime_minutes: 300

# === Ideas ===
# Number of ideas to generate in a batch when the todo list is empty.
idea_generation_batch_size: 5

# === Git ===
# Commit message prefix for target repo commits.
commit_prefix: perf

# Only commit changed files under these path prefixes (comma-separated).
# Prevents accidentally committing unrelated WIP changes in the target repo.
commit_scope: src/

# === AI Providers ===
# Supported providers: claude, gemini
# Comma-separated list of providers to permanently disable.
disabled_providers:

# Maximum time (seconds) to wait for an LLM response before timing out.
llm_timeout: 3600

# How many times to retry after all providers fail in a single call.
# Each retry waits 2 hours for provider quota to reset.
# 0 = fail immediately (useful for testing). Set high for unattended runs.
providers_retry_limit: 1000
"""

INSTRUCTIONS_TEMPLATE = """\
# Optimisation Instructions

<!-- Describe what to optimise and any constraints. This file is passed
     verbatim to the LLM for every task. -->

Optimise the performance of the target file(s). Focus on algorithmic
improvements and reducing unnecessary computation.
"""

LEARNINGS_TEMPLATE = """\
## What works

## What to avoid
"""