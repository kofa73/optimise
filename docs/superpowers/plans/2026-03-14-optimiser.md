# Optimiser Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a configurable Python tool that automates performance optimisation via an LLM-driven generate→implement→build→test→benchmark loop across two git repositories.

**Architecture:** Modular Python package (`optimise/`) with separate modules for settings, state management, git operations, benchmark parsing, AI routing, prompt building, and orchestration. Entry point is `optimise.py`. TDD throughout — tests first, then implementation. All deterministic work (maths, file ops, state transitions) in Python; LLM restricted to code generation/editing and natural language.

**Tech Stack:** Python 3.10+, pytest, no external dependencies beyond standard library. LLM interaction via `claude` and `gemini` CLI tools (subprocess).

**Spec:** `docs/superpowers/specs/2026-03-14-optimiser-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `optimise.py` | Entry point — parse `init` / `run` subcommands, delegate to `cli.py` |
| `optimise/__init__.py` | Package marker |
| `optimise/settings.py` | Parse `settings.conf`, validate, provide defaults, generate template for `init` |
| `optimise/state.py` | Idea file CRUD, filename sanitisation, dedup, directory transitions, learnings I/O |
| `optimise/git.py` | Branch resolution, commit, rollback, dirty checks — for both repos |
| `optimise/benchmark.py` | Parse benchmark output lines, convergence loop, perf log formatting, success evaluation |
| `optimise/ai.py` | AIRouter — provider registry, failover, invocation, timeout |
| `optimise/prompts.py` | Build prompts for generate, select, implement, review roles |
| `optimise/runner.py` | Main state machine: startup recovery, baseline, main loop, termination |
| `optimise/cli.py` | `init` scaffolding + `run` entry point (wires everything together) |
| `tests/conftest.py` | Shared fixtures (tmp dirs, git repo helpers) |
| `tests/test_settings.py` | Settings parsing, validation, defaults, init template |
| `tests/test_state.py` | Idea lifecycle, filename sanitisation, dedup, transitions |
| `tests/test_git.py` | Branch logic, commit, rollback, dirty detection |
| `tests/test_benchmark.py` | Output parsing, convergence, stats, success evaluation, perf log formatting |
| `tests/test_ai.py` | Provider selection, failover, disable/reset |
| `tests/test_prompts.py` | Prompt construction for each role |
| `tests/test_runner.py` | State machine transitions, startup recovery, termination |
| `tests/test_cli.py` | Init scaffolding, end-to-end CLI |

---

## Chunk 1: Foundation (Settings + State + Git)

### Task 1: Project scaffolding and test infrastructure

**Files:**
- Create: `optimise.py`
- Create: `optimise/__init__.py`
- Create: `tests/conftest.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Create `pyproject.toml` with pytest config**

```toml
[project]
name = "optimiser"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create package marker**

```python
# optimise/__init__.py
```

- [ ] **Step 3: Create entry point stub**

```python
#!/usr/bin/env python3
"""Optimiser — automated performance optimisation via LLM."""
import sys

def main():
    print("optimise: not yet implemented")
    sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create shared test fixtures**

```python
# tests/conftest.py
import os
import subprocess
import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    """A temporary directory for test files."""
    return tmp_path


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repo with an initial commit."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    # Create initial commit on main
    marker = tmp_path / ".gitkeep"
    marker.write_text("")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


@pytest.fixture
def script_repo(tmp_path):
    """Create a script repo with the standard directory structure."""
    for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "learnings.md").write_text("## What works\n\n## What to avoid\n")
    (tmp_path / "instructions.md").write_text("Optimise the target for performance.\n")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path
```

- [ ] **Step 5: Verify pytest discovers no tests (sanity check)**

Run: `cd /workspace/optimiser && python -m pytest --co -q`
Expected: `no tests ran`

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml optimise.py optimise/__init__.py tests/conftest.py
git commit -m "scaffold: project structure and test fixtures"
```

---

### Task 2: Settings parsing and validation

**Files:**
- Create: `tests/test_settings.py`
- Create: `optimise/settings.py`

- [ ] **Step 1: Write failing tests for settings parsing**

```python
# tests/test_settings.py
import pytest
from optimise.settings import parse_settings, validate_settings, SettingsError


class TestParseSettings:
    def test_parses_key_value_pairs(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo: /some/path\nbuild_cmd: make\n")
        result = parse_settings(str(f))
        assert result["target_repo"] == "/some/path"
        assert result["build_cmd"] == "make"

    def test_ignores_comments(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("# this is a comment\ntarget_repo: /path\n")
        result = parse_settings(str(f))
        assert "this" not in result
        assert result["target_repo"] == "/path"

    def test_ignores_blank_lines(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo: /path\n\n\nbuild_cmd: make\n")
        result = parse_settings(str(f))
        assert len(result) == 2

    def test_strips_whitespace_from_values(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo:   /some/path   \n")
        result = parse_settings(str(f))
        assert result["target_repo"] == "/some/path"

    def test_empty_value(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("quality_cmd:\n")
        result = parse_settings(str(f))
        assert result["quality_cmd"] == ""

    def test_preserves_colons_in_values(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("build_cmd: make -C /path:to:thing\n")
        result = parse_settings(str(f))
        assert result["build_cmd"] == "make -C /path:to:thing"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_settings("/nonexistent/path")


class TestValidateSettings:
    def _make_valid_settings(self, tmp_path):
        """Return a minimal valid settings dict."""
        target = tmp_path / "target"
        target.mkdir()
        src = target / "src" / "main.c"
        src.parent.mkdir(parents=True)
        src.write_text("int main() {}")
        instr = tmp_path / "instructions.md"
        instr.write_text("do stuff")
        return {
            "target_repo": str(target),
            "branch": "optimise-test",
            "optimisation_target": "src/main.c",
            "instructions": str(instr),
            "build_cmd": "make",
            "bench_cmd": "python bench.py",
            "quality_cmd": "",
            "min_improvement_pct": "0.5",
            "individual_regression_tradeoff": "2",
            "early_abort_regression_pct": "10",
            "num_warmup_iterations": "0",
            "benchmark_convergence_threshold_pct": "0.1",
            "benchmark_convergence_tail_runs": "5",
            "max_retries": "5",
            "max_iterations": "50",
            "max_consecutive_perf_failures": "5",
            "max_runtime_minutes": "300",
            "review_frequency": "3",
            "min_ideas": "5",
            "max_dedup_attempts": "10",
            "commit_prefix": "perf",
        }

    def test_valid_settings_pass(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["target_repo"] == settings["target_repo"]
        # Numeric values are converted
        assert result["min_improvement_pct"] == 0.5
        assert result["max_retries"] == 5

    def test_missing_target_repo_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        del settings["target_repo"]
        with pytest.raises(SettingsError, match="target_repo"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_nonexistent_target_repo_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["target_repo"] = "/nonexistent/repo"
        with pytest.raises(SettingsError, match="target_repo"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_missing_build_cmd_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["build_cmd"] = ""
        with pytest.raises(SettingsError, match="build_cmd"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_missing_bench_cmd_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["bench_cmd"] = ""
        with pytest.raises(SettingsError, match="bench_cmd"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_invalid_numeric_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["min_improvement_pct"] = "not_a_number"
        with pytest.raises(SettingsError, match="min_improvement_pct"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_empty_quality_cmd_is_ok(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["quality_cmd"] = ""
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["quality_cmd"] == ""

    def test_nonexistent_optimisation_target_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["optimisation_target"] = "nonexistent.c"
        with pytest.raises(SettingsError, match="optimisation_target"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_comma_separated_targets(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        target = tmp_path / "target"
        (target / "src" / "other.c").write_text("void f() {}")
        settings["optimisation_target"] = "src/main.c, src/other.c"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["optimisation_target"] == ["src/main.c", "src/other.c"]

    def test_single_target_returns_list(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["optimisation_target"] = "src/main.c"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["optimisation_target"] == ["src/main.c"]

    def test_nonexistent_instructions_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["instructions"] = "nonexistent.md"
        with pytest.raises(SettingsError, match="instructions"):
            validate_settings(settings, script_repo=str(tmp_path))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'optimise.settings'`

- [ ] **Step 3: Implement settings module**

```python
# optimise/settings.py
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
    "min_improvement_pct", "individual_regression_tradeoff",
    "early_abort_regression_pct", "benchmark_convergence_threshold_pct",
]

# Keys that are converted to int
_INT_KEYS = [
    "num_warmup_iterations", "benchmark_convergence_tail_runs",
    "max_retries", "max_iterations", "max_consecutive_perf_failures",
    "max_runtime_minutes", "review_frequency", "min_ideas", "max_dedup_attempts",
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
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"(\w[\w-]*):\s*(.*)", line)
            if m:
                config[m.group(1)] = m.group(2).strip()
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

# If any individual row regresses, sum improvement must also be at least
# this multiplier times the worst individual row regression percent.
# 0 = ignore individual regressions; very large value = reject any regression.
individual_regression_tradeoff: 2

# Abort benchmark early if first real run regresses by more than this (percent).
early_abort_regression_pct: 10

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

# === Strategy Review ===
# Run learnings review every N iterations.
review_frequency: 3

# === Ideas ===
# Minimum number of ideas to maintain in ideas/todo.
min_ideas: 5

# Maximum dedup attempts when generating ideas before declaring exhaustion.
max_dedup_attempts: 10

# === Git ===
# Commit message prefix for target repo commits.
commit_prefix: perf
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_settings.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/settings.py tests/test_settings.py
git commit -m "feat: settings parsing and validation"
```

---

### Task 3: State management — filename sanitisation and idea CRUD

**Files:**
- Create: `tests/test_state.py`
- Create: `optimise/state.py`

- [ ] **Step 1: Write failing tests for filename sanitisation**

```python
# tests/test_state.py
import pytest
from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \
    read_idea, append_outcome, all_idea_titles, dedup_title, clean_errors


class TestSanitiseFilename:
    def test_clean_name(self):
        assert sanitise_filename("precompute-half_anisotropy") == "precompute-half_anisotropy.md"

    def test_strips_extension(self):
        assert sanitise_filename("my-idea.txt") == "my-idea.md"

    def test_strips_md_extension(self):
        assert sanitise_filename("my-idea.md") == "my-idea.md"

    def test_replaces_spaces(self):
        assert sanitise_filename("my great idea") == "my_great_idea.md"

    def test_replaces_special_chars(self):
        assert sanitise_filename("idea: improve (speed) by 50%!") == "idea__improve__speed__by_50__.md"

    def test_complex_llm_output(self):
        name = "precompute half anisotropy outside loop, to improve gradient calculation speed.txt"
        result = sanitise_filename(name)
        assert result == "precompute_half_anisotropy_outside_loop__to_improve_gradient_calculation_speed.md"
        # Verify only allowed chars (plus .md extension)
        stem = result[:-3]
        assert all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in stem)


class TestCreateIdea:
    def test_creates_file_in_todo(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "my-idea", "Improve loop performance\n\nDetails here.")
        assert path.endswith(".md")
        assert "ideas/todo/" in path
        with open(path) as f:
            assert f.read() == "Improve loop performance\n\nDetails here."

    def test_sanitises_filename(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "bad name with spaces.txt", "Title\n\nBody")
        assert "bad_name_with_spaces.md" in path


class TestListIdeas:
    def test_lists_todo_ideas(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        (todo / "idea-a.md").write_text("Idea A title\n\nBody")
        (todo / "idea-b.md").write_text("Idea B title\n\nBody")
        result = list_ideas(str(tmp_path), "todo")
        assert sorted(result) == ["idea-a.md", "idea-b.md"]

    def test_empty_directory(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        assert list_ideas(str(tmp_path), "todo") == []


class TestMoveIdea:
    def test_moves_between_directories(self, tmp_path):
        for d in ["ideas/todo", "ideas/coding"]:
            (tmp_path / d).mkdir(parents=True)
        src = tmp_path / "ideas" / "todo" / "my-idea.md"
        src.write_text("content")
        move_idea(str(tmp_path), "my-idea.md", "todo", "coding")
        assert not src.exists()
        dst = tmp_path / "ideas" / "coding" / "my-idea.md"
        assert dst.exists()
        assert dst.read_text() == "content"


class TestReadIdea:
    def test_reads_title_and_body(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        (todo / "idea.md").write_text("The title line\n\nThe body text.\nMore body.")
        title, body = read_idea(str(tmp_path), "todo", "idea.md")
        assert title == "The title line"
        assert "The body text." in body


class TestAppendOutcome:
    def test_appends_success(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        append_outcome(str(tmp_path), "idea.md", "improvement",
                       commit_hash="abc123",
                       perf_summary="Reduced sum(user) from 10.0s to 9.0s (~10.0% improvement)")
        content = (done / "idea.md").read_text()
        assert "outcome: improvement" in content
        assert "commit: abc123" in content
        assert "Reduced sum(user)" in content

    def test_appends_failure(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        append_outcome(str(tmp_path), "idea.md", "build failure")
        content = (done / "idea.md").read_text()
        assert "outcome: build failure" in content
        assert "commit:" not in content


class TestAllIdeaTitles:
    def test_collects_from_all_dirs(self, tmp_path):
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (tmp_path / d).mkdir(parents=True)
        (script_repo / "ideas" / "todo" / "a.md").write_text("Title A\n\nBody")
        (script_repo / "ideas" / "done" / "b.md").write_text("Title B\n\nBody")
        titles = all_idea_titles(str(tmp_path))
        assert set(titles) == {"Title A", "Title B"}


class TestDedupTitle:
    def test_exact_match_is_duplicate(self):
        from optimise.state import dedup_title
        assert dedup_title("My Idea", ["My Idea", "Other"]) is True

    def test_case_insensitive(self):
        from optimise.state import dedup_title
        assert dedup_title("my idea", ["My Idea"]) is True

    def test_no_match(self):
        from optimise.state import dedup_title
        assert dedup_title("New Idea", ["Old Idea"]) is False

    def test_empty_list(self):
        from optimise.state import dedup_title
        assert dedup_title("Idea", []) is False


class TestCleanErrors:
    def test_removes_existing_file(self, tmp_path):
        from optimise.state import clean_errors
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        (coding / "errors.txt").write_text("some error")
        clean_errors(str(tmp_path))
        assert not (coding / "errors.txt").exists()

    def test_no_error_if_missing(self, tmp_path):
        from optimise.state import clean_errors
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        clean_errors(str(tmp_path))  # should not raise


class TestSaveErrors:
    def test_writes_error_file(self, tmp_path):
        from optimise.state import save_errors
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        save_errors(str(tmp_path), "error: undefined reference")
        assert (coding / "errors.txt").read_text() == "error: undefined reference"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_state.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'optimise.state'`

- [ ] **Step 3: Implement state module**

```python
# optimise/state.py
"""Idea lifecycle management and file operations."""
import os
import re


def sanitise_filename(name):
    """Sanitise an LLM-proposed idea filename.

    1. Strip any file extension.
    2. Replace characters not in [a-zA-Z0-9_-] with underscore.
    3. Append .md
    """
    # Strip extension if present
    base, ext = os.path.splitext(name)
    if ext:
        name = base
    # Replace disallowed characters
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    return name + ".md"


def create_idea(script_repo, raw_name, content):
    """Create an idea file in ideas/todo/.

    Returns the absolute path to the created file.
    """
    filename = sanitise_filename(raw_name)
    path = os.path.join(script_repo, "ideas", "todo", filename)
    with open(path, "w") as f:
        f.write(content)
    return path


def list_ideas(script_repo, subdir):
    """List idea filenames in ideas/<subdir>/. Returns list of filenames."""
    d = os.path.join(script_repo, "ideas", subdir)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".md"))


def move_idea(script_repo, filename, from_dir, to_dir):
    """Move an idea file between idea subdirectories."""
    src = os.path.join(script_repo, "ideas", from_dir, filename)
    dst = os.path.join(script_repo, "ideas", to_dir, filename)
    os.rename(src, dst)


def read_idea(script_repo, subdir, filename):
    """Read an idea file. Returns (title, body) where title is line 1."""
    path = os.path.join(script_repo, "ideas", subdir, filename)
    with open(path) as f:
        content = f.read()
    lines = content.split("\n", 1)
    title = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    return title, body


def append_outcome(script_repo, filename, outcome, commit_hash=None, perf_summary=None):
    """Append outcome to an idea file in ideas/done/."""
    path = os.path.join(script_repo, "ideas", "done", filename)
    with open(path, "a") as f:
        f.write(f"\noutcome: {outcome}\n")
        if commit_hash:
            f.write(f"commit: {commit_hash}\n")
        if perf_summary:
            f.write(f"{perf_summary}\n")


def all_idea_titles(script_repo):
    """Collect titles (first lines) from all idea files across all subdirs."""
    titles = []
    for subdir in ["todo", "coding", "testing", "done"]:
        for filename in list_ideas(script_repo, subdir):
            title, _ = read_idea(script_repo, subdir, filename)
            if title:
                titles.append(title)
    return titles


def dedup_title(title, existing_titles):
    """Check if a title is a case-insensitive duplicate of any existing title.

    Returns True if it IS a duplicate (should be discarded).
    """
    lower = title.lower()
    return any(lower == t.lower() for t in existing_titles)


def clean_errors(script_repo):
    """Remove ideas/coding/errors.txt if it exists."""
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    if os.path.exists(path):
        os.remove(path)


def save_errors(script_repo, error_output):
    """Save build/quality error output to ideas/coding/errors.txt."""
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    with open(path, "w") as f:
        f.write(error_output)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_state.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/state.py tests/test_state.py
git commit -m "feat: idea state management and filename sanitisation"
```

---

### Task 4: Git operations

**Files:**
- Create: `tests/test_git.py`
- Create: `optimise/git.py`

- [ ] **Step 1: Write failing tests for git module**

```python
# tests/test_git.py
import subprocess
import pytest
from optimise.git import GitRepo, GitError


class TestGitRepo:
    def test_current_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        # Git init creates "main" or "master" depending on config
        branch = repo.current_branch()
        assert branch in ("main", "master")

    def test_is_dirty_clean_repo(self, git_repo):
        repo = GitRepo(str(git_repo))
        assert not repo.is_dirty()

    def test_is_dirty_modified_file(self, git_repo):
        (git_repo / ".gitkeep").write_text("modified")
        repo = GitRepo(str(git_repo))
        assert repo.is_dirty()

    def test_is_dirty_untracked_file(self, git_repo):
        (git_repo / "newfile.txt").write_text("new")
        repo = GitRepo(str(git_repo))
        # Untracked files should NOT count as dirty
        assert not repo.is_dirty()

    def test_branch_exists(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        assert repo.branch_exists(default)
        assert not repo.branch_exists("nonexistent-branch")

    def test_create_and_switch_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("test-branch")
        assert repo.current_branch() == "test-branch"

    def test_switch_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        repo.create_branch("other")
        repo.switch_branch(default)
        assert repo.current_branch() == default
        repo.switch_branch("other")
        assert repo.current_branch() == "other"

    def test_rollback(self, git_repo):
        target = git_repo / "file.txt"
        target.write_text("original")
        subprocess.run(["git", "add", "file.txt"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add file"], cwd=git_repo, check=True, capture_output=True)
        target.write_text("modified")
        repo = GitRepo(str(git_repo))
        assert repo.is_dirty()
        repo.rollback()
        assert not repo.is_dirty()
        assert target.read_text() == "original"

    def test_rollback_removes_new_files(self, git_repo):
        (git_repo / "newfile.txt").write_text("new")
        repo = GitRepo(str(git_repo))
        repo.rollback()
        assert not (git_repo / "newfile.txt").exists()

    def test_commit_and_get_hash(self, git_repo):
        target = git_repo / "file.txt"
        target.write_text("content")
        repo = GitRepo(str(git_repo))
        repo.commit(["file.txt"], "test: add file", "Extended body\n\nDetails.")
        hash = repo.get_commit_hash()
        assert len(hash) >= 7
        assert not repo.is_dirty()

    def test_default_branch_detection(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.default_branch()
        assert default in ("main", "master")


class TestBranchResolution:
    def test_already_on_target(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        repo.create_branch("optimise-test")
        # Should succeed — already on target
        repo.resolve_branch("optimise-test")
        assert repo.current_branch() == "optimise-test"

    def test_on_default_clean_creates_and_switches(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.resolve_branch("optimise-new")
        assert repo.current_branch() == "optimise-new"

    def test_on_default_dirty_fails(self, git_repo):
        (git_repo / ".gitkeep").write_text("dirty")
        repo = GitRepo(str(git_repo))
        with pytest.raises(GitError, match="uncommitted changes"):
            repo.resolve_branch("optimise-test")

    def test_on_wrong_branch_fails(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("some-other-branch")
        with pytest.raises(GitError, match="expected"):
            repo.resolve_branch("optimise-test")

    def test_on_default_target_exists_switches(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("optimise-test")
        default = repo.default_branch()
        repo.switch_branch(default)
        repo.resolve_branch("optimise-test")
        assert repo.current_branch() == "optimise-test"


class TestCommitAll:
    def test_stages_and_commits_all(self, git_repo):
        (git_repo / "newfile.txt").write_text("content")
        repo = GitRepo(str(git_repo))
        repo.commit_all("test: add everything")
        assert not repo.is_dirty()
        assert not (git_repo / "newfile.txt").read_text() == ""  # file exists

    def test_noop_when_nothing_to_commit(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.commit_all("test: nothing")  # should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_git.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'optimise.git'`

- [ ] **Step 3: Implement git module**

```python
# optimise/git.py
"""Git operations for target and script repositories."""
import os
import subprocess


class GitError(Exception):
    """Raised on git operation failures."""
    pass


class GitRepo:
    """Git operations on a single repository."""

    def __init__(self, path):
        self.path = path

    def _run(self, args, check=True, capture=True):
        """Run a git command in this repo."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.path,
            capture_output=capture,
            text=True,
        )
        if check and result.returncode != 0:
            raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result

    def current_branch(self):
        """Return the current branch name."""
        result = self._run(["rev-parse", "--abbrev-ref", "HEAD"])
        return result.stdout.strip()

    def default_branch(self):
        """Detect the default branch (main/master).

        Tries remote HEAD first, falls back to local branch names.
        """
        # Try remote HEAD
        result = self._run(["symbolic-ref", "refs/remotes/origin/HEAD"], check=False)
        if result.returncode == 0:
            ref = result.stdout.strip()
            return ref.split("/")[-1]
        # Fallback: check local branches
        for name in ("main", "master"):
            if self.branch_exists(name):
                return name
        # Last resort: current branch
        return self.current_branch()

    def is_dirty(self):
        """Check for uncommitted changes to tracked files."""
        result = self._run(["diff", "--quiet", "HEAD"], check=False)
        if result.returncode != 0:
            return True
        # Also check staged changes
        result = self._run(["diff", "--cached", "--quiet", "HEAD"], check=False)
        return result.returncode != 0

    def branch_exists(self, name):
        """Check if a local branch exists."""
        result = self._run(["rev-parse", "--verify", f"refs/heads/{name}"], check=False)
        return result.returncode == 0

    def create_branch(self, name):
        """Create a new branch and switch to it."""
        self._run(["checkout", "-b", name])

    def switch_branch(self, name):
        """Switch to an existing branch."""
        self._run(["checkout", name])

    def rollback(self):
        """Restore all tracked files to HEAD and remove untracked files."""
        self._run(["checkout", "HEAD", "--", "."])
        self._run(["clean", "-fd"])

    def commit(self, files, title, body=None):
        """Stage specific files and commit.

        Args:
            files: list of relative file paths to stage
            title: commit message first line
            body: optional extended commit body (appended after blank line)
        """
        for f in files:
            self._run(["add", f])
        message = title
        if body:
            message = f"{title}\n\n{body}"
        self._run(["commit", "-m", message])

    def commit_all(self, message):
        """Stage all changes and commit."""
        self._run(["add", "-A"])
        # Check if there is anything to commit
        result = self._run(["diff", "--cached", "--quiet", "HEAD"], check=False)
        if result.returncode == 0:
            return  # Nothing to commit
        self._run(["commit", "-m", message])

    def get_commit_hash(self):
        """Return short hash of HEAD."""
        result = self._run(["rev-parse", "--short", "HEAD"])
        return result.stdout.strip()

    def resolve_branch(self, target_branch):
        """Ensure we are on the target branch per the spec's branch resolution logic.

        If on default branch and clean: create target if needed, switch.
        If on target: OK.
        Otherwise: raise GitError.
        """
        current = self.current_branch()

        if current == target_branch:
            return

        default = self.default_branch()
        if current == default:
            if self.is_dirty():
                raise GitError(
                    f"Repository at {self.path} has uncommitted changes on "
                    f"{default}. Please clean up first."
                )
            if not self.branch_exists(target_branch):
                self.create_branch(target_branch)
            else:
                self.switch_branch(target_branch)
        else:
            raise GitError(
                f"Repository at {self.path} is on branch '{current}', "
                f"expected '{target_branch}' or '{default}'. Please clean up first."
            )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_git.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/git.py tests/test_git.py
git commit -m "feat: git operations with branch resolution"
```

---

## Chunk 2: Benchmark Module

### Task 5: Benchmark output parsing

**Files:**
- Create: `tests/test_benchmark.py`
- Create: `optimise/benchmark.py`

- [ ] **Step 1: Write failing tests for output parsing**

```python
# tests/test_benchmark.py
import pytest
from optimise.benchmark import parse_bench_output, BenchmarkError


class TestParseBenchOutput:
    def test_single_line_user_only(self):
        rows = parse_bench_output("user=0.561\n")
        assert len(rows) == 1
        assert rows[0]["user"] == pytest.approx(0.561)

    def test_single_line_multiple_labels(self):
        rows = parse_bench_output("user=0.234, cpu=0.051, gpu=0.180\n")
        assert len(rows) == 1
        assert rows[0]["user"] == pytest.approx(0.234)
        assert rows[0]["cpu"] == pytest.approx(0.051)
        assert rows[0]["gpu"] == pytest.approx(0.180)

    def test_multiple_lines(self):
        text = "user=0.561, cpu=5.372\nuser=0.123\nuser=0.234, cpu=0.051, gpu=0.180\n"
        rows = parse_bench_output(text)
        assert len(rows) == 3
        assert rows[0]["user"] == pytest.approx(0.561)
        assert rows[1]["user"] == pytest.approx(0.123)
        assert "cpu" not in rows[1]
        assert rows[2]["gpu"] == pytest.approx(0.180)

    def test_missing_user_raises(self):
        with pytest.raises(BenchmarkError, match="user"):
            parse_bench_output("cpu=0.5\n")

    def test_empty_output_raises(self):
        with pytest.raises(BenchmarkError):
            parse_bench_output("")

    def test_malformed_value_raises(self):
        with pytest.raises(BenchmarkError):
            parse_bench_output("user=abc\n")

    def test_ignores_blank_lines(self):
        text = "user=0.1\n\nuser=0.2\n"
        rows = parse_bench_output(text)
        assert len(rows) == 2

    def test_no_spaces_around_equals(self):
        rows = parse_bench_output("user=0.5,cpu=1.0\n")
        assert rows[0]["user"] == pytest.approx(0.5)
        assert rows[0]["cpu"] == pytest.approx(1.0)

    def test_leading_dot_value(self):
        rows = parse_bench_output("user=.234, cpu=0.051\n")
        assert rows[0]["user"] == pytest.approx(0.234)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py::TestParseBenchOutput -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement parsing**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py::TestParseBenchOutput -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/benchmark.py tests/test_benchmark.py
git commit -m "feat: benchmark output parsing"
```

---

### Task 6: Element-wise best tracking and convergence logic

**Files:**
- Modify: `tests/test_benchmark.py`
- Modify: `optimise/benchmark.py`

- [ ] **Step 1: Write failing tests for element-wise best and convergence**

Append to `tests/test_benchmark.py`:

```python
from optimise.benchmark import update_element_best, check_convergence, ConvergenceState


class TestUpdateElementBest:
    def test_first_run_sets_best(self):
        rows = [{"user": 0.5, "cpu": 1.0}, {"user": 0.3}]
        best = update_element_best(None, rows)
        assert best[0]["user"] == pytest.approx(0.5)
        assert best[0]["cpu"] == pytest.approx(1.0)
        assert best[1]["user"] == pytest.approx(0.3)

    def test_keeps_minimum(self):
        best = [{"user": 0.5, "cpu": 1.0}, {"user": 0.3}]
        new = [{"user": 0.4, "cpu": 1.1}, {"user": 0.35}]
        result = update_element_best(best, new)
        assert result[0]["user"] == pytest.approx(0.4)  # improved
        assert result[0]["cpu"] == pytest.approx(1.0)    # kept old
        assert result[1]["user"] == pytest.approx(0.3)   # kept old

    def test_wrong_row_count_raises(self):
        best = [{"user": 0.5}]
        new = [{"user": 0.4}, {"user": 0.3}]
        with pytest.raises(BenchmarkError, match="row"):
            update_element_best(best, new)


class TestConvergence:
    def test_initial_state(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        assert state.tail_counter == 0
        assert state.reference_sum is None

    def test_first_update_sets_reference(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        assert state.reference_sum == pytest.approx(10.0)
        assert state.tail_counter == 0
        assert not state.converged

    def test_significant_improvement_resets_tail(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        state.update(10.0)  # no change, tail=1
        state.update(9.5)   # big drop, reset
        assert state.tail_counter == 0
        assert state.reference_sum == pytest.approx(9.5)

    def test_converges_after_tail_runs(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        state.update(10.0)  # tail=1
        state.update(10.0)  # tail=2
        state.update(10.0)  # tail=3
        assert state.converged

    def test_tiny_improvement_counts_as_tail(self):
        state = ConvergenceState(threshold_pct=1.0, tail_runs=2)
        state.update(10.0)
        state.update(9.95)  # 0.5% < 1.0% threshold → tail=1
        state.update(9.94)  # still < 1.0% from reference → tail=2
        assert state.converged
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py::TestUpdateElementBest tests/test_benchmark.py::TestConvergence -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement element-wise best and convergence**

Append to `optimise/benchmark.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/benchmark.py tests/test_benchmark.py
git commit -m "feat: element-wise best tracking and convergence"
```

---

### Task 7: Success evaluation

**Files:**
- Modify: `tests/test_benchmark.py`
- Modify: `optimise/benchmark.py`

- [ ] **Step 1: Write failing tests for success evaluation**

Append to `tests/test_benchmark.py`:

```python
from optimise.benchmark import evaluate_success


class TestEvaluateSuccess:
    def test_clear_improvement_passes(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 9.0}, {"user": 9.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert ok
        assert pct == pytest.approx(10.0)

    def test_below_min_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 9.96}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok
        assert "noise" in detail.lower() or "min" in detail.lower()

    def test_regression_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.5}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok

    def test_individual_regression_exceeds_tradeoff_fails(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.5}]  # row 2 regressed 5%, sum improved 7.5%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        # 7.5% improvement >= 2 * 5% regression = 10% → FAILS tradeoff
        assert not ok

    def test_individual_regression_passes_with_enough_improvement(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 7.0}, {"user": 10.2}]  # row 2 regressed 2%, sum improved 14%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        # 14% >= 2 * 2% = 4% → PASSES
        assert ok

    def test_zero_tradeoff_ignores_individual_regression(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 5.0}, {"user": 14.0}]  # row 2 regressed 40%, sum improved 5%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=0
        )
        assert ok

    def test_no_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py::TestEvaluateSuccess -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement success evaluation**

Append to `optimise/benchmark.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/benchmark.py tests/test_benchmark.py
git commit -m "feat: benchmark success evaluation"
```

---

### Task 8: Performance log formatting

**Files:**
- Modify: `tests/test_benchmark.py`
- Modify: `optimise/benchmark.py`

- [ ] **Step 1: Write failing tests for perf log formatting**

Append to `tests/test_benchmark.py`:

```python
from optimise.benchmark import format_perf_log, parse_perf_log


class TestFormatPerfLog:
    def test_basic_format(self):
        rows = [
            {"user": 0.551, "cpu": 5.372},
            {"user": 0.123},
            {"user": 0.234, "cpu": 0.051, "gpu": 0.180},
        ]
        text = format_perf_log(rows)
        assert "# Individual timings" in text
        assert "# Totals" in text
        assert "# Averages" in text
        assert "| user | cpu | gpu |" in text
        # Check totals: user=0.908, cpu=5.423, gpu=0.180
        assert "0.908" in text
        assert "5.423" in text

    def test_single_row(self):
        rows = [{"user": 1.5}]
        text = format_perf_log(rows)
        assert "| user |" in text
        assert "1.5" in text or "1.500" in text

    def test_averages_exclude_missing(self):
        rows = [
            {"user": 1.0, "cpu": 4.0},
            {"user": 2.0},
        ]
        text = format_perf_log(rows)
        # Average of user: (1.0+2.0)/2 = 1.5
        # Average of cpu: 4.0/1 = 4.0 (only 1 row has cpu)
        assert "1.5" in text or "1.500" in text


class TestParsePerfLog:
    def test_round_trip(self):
        rows = [{"user": 0.551, "cpu": 5.372}, {"user": 0.123}]
        text = format_perf_log(rows)
        parsed = parse_perf_log(text)
        assert len(parsed) == 2
        assert parsed[0]["user"] == pytest.approx(0.551)
        assert parsed[0]["cpu"] == pytest.approx(5.372)
        assert parsed[1]["user"] == pytest.approx(0.123)
        assert "cpu" not in parsed[1]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py::TestFormatPerfLog tests/test_benchmark.py::TestParsePerfLog -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement perf log formatting and parsing**

Append to `optimise/benchmark.py`:

```python
def _max_decimal_places(rows):
    """Find the maximum decimal places used across all values."""
    max_dp = 0
    for row in rows:
        for v in row.values():
            s = f"{v:g}"
            if "." in s:
                dp = len(s.split(".")[1])
                max_dp = max(max_dp, dp)
    return max(max_dp, 1)  # at least 1


def _all_labels(rows):
    """Collect all labels in order (user first, then sorted rest)."""
    labels = set()
    for row in rows:
        labels.update(row.keys())
    labels.discard("user")
    return ["user"] + sorted(labels)


def format_perf_log(rows):
    """Format benchmark rows into a markdown perf log.

    Contains three tables: Individual timings, Totals, Averages.
    """
    labels = _all_labels(rows)
    dp = _max_decimal_places(rows)

    def fmt(v):
        return f"{v:.{dp}f}"

    def table(header, data_rows):
        lines = [f"| {' | '.join(labels)} |"]
        lines.append(f"| {' | '.join('----' for _ in labels)} |")
        for row in data_rows:
            cells = []
            for label in labels:
                if label in row:
                    cells.append(fmt(row[label]))
                else:
                    cells.append("")
            lines.append(f"| {' | '.join(cells)} |")
        return f"# {header}\n" + "\n".join(lines)

    # Totals: missing = 0
    totals = {}
    for label in labels:
        totals[label] = sum(row.get(label, 0) for row in rows)

    # Averages: missing excluded
    averages = {}
    for label in labels:
        values = [row[label] for row in rows if label in row]
        if values:
            averages[label] = sum(values) / len(values)

    sections = [
        table("Individual timings", rows),
        table("Totals", [totals]),
        table("Averages", [averages]),
    ]
    return "\n\n".join(sections) + "\n"


def parse_perf_log(text):
    """Parse the Individual timings table from a perf log back into row dicts.

    Only parses the first table (Individual timings).
    """
    rows = []
    in_table = False
    labels = []

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("# Individual timings"):
            in_table = True
            continue
        if in_table and line.startswith("#"):
            break  # Next section
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not labels:
            labels = cells
            continue
        if all(c.startswith("-") for c in cells):
            continue  # separator row
        row = {}
        for label, cell in zip(labels, cells):
            cell = cell.strip()
            if cell:
                row[label] = float(cell)
        if row:
            rows.append(row)

    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_benchmark.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/benchmark.py tests/test_benchmark.py
git commit -m "feat: performance log formatting and parsing"
```

---

## Chunk 3: AI, Prompts, CLI, and Runner

### Task 9: AI module — provider routing and failover

**Files:**
- Create: `tests/test_ai.py`
- Create: `optimise/ai.py`

- [ ] **Step 1: Write failing tests for AI routing**

```python
# tests/test_ai.py
import pytest
from unittest.mock import patch, MagicMock
from optimise.ai import AIRouter


class TestAIRouter:
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_discovers_available_providers(self, mock_which):
        router = AIRouter(providers=["claude"])
        assert router.has_providers

    @patch("shutil.which", return_value=None)
    def test_no_providers_exits(self, mock_which):
        with pytest.raises(SystemExit):
            AIRouter(providers=["claude"])

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_disable_provider(self, mock_which):
        router = AIRouter(providers=["claude"])
        router.disable_provider("claude")
        assert not router.has_providers

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_reset_providers(self, mock_which):
        router = AIRouter(providers=["claude"])
        router.disable_provider("claude")
        router.reset_providers()
        assert router.has_providers

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_call_returns_stdout_on_success(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="result text", returncode=0)
        router = AIRouter(providers=["claude"])
        stdout, rc, provider = router.call("test prompt", allow_edits=False)
        assert stdout == "result text"
        assert rc == 0
        assert provider == "claude"

    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_call_disables_on_failure(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="", returncode=1)
        router = AIRouter(providers=["claude", "gemini"])
        # Both will fail; after two failures it should wait
        # We don't want to actually wait 300s in tests, so mock time.sleep
        with patch("time.sleep"):
            # Call with a timeout to prevent infinite loop
            mock_run.side_effect = [
                MagicMock(stdout="", returncode=1),  # first provider fails
                MagicMock(stdout="", returncode=1),  # second provider fails
                MagicMock(stdout="ok", returncode=0),  # retry succeeds
            ]
            stdout, rc, provider = router.call("test", allow_edits=False)
        assert stdout == "ok"
        assert rc == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_ai.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement AI module**

```python
# optimise/ai.py
"""AI provider routing with failover between claude and gemini CLIs."""
import os
import subprocess
import shutil
import sys
import time
import random
import logging

log = logging.getLogger("optimiser")

PROVIDERS = {
    "claude": {
        "cmd_text": lambda model: [
            "claude", "--print", "--model", model,
            "--dangerously-skip-permissions", "--verbose",
        ],
        "cmd_edit": lambda model: [
            "claude", "--print", "--model", model,
            "--dangerously-skip-permissions", "--verbose",
            "--allowedTools", "Read", "Edit",
        ],
        "env_cleanup": ["CLAUDECODE"],
        "models": {"best": "opus", "normal": "sonnet"},
        "uses_stdin": True,
    },
    "gemini": {
        "cmd_text": lambda model: [
            "gemini", "--model", model,
            "Follow the instructions in the provided text.",
        ],
        "cmd_edit": lambda model: [
            "gemini", "--model", model, "--approval-mode=yolo",
            "Follow the instructions in the provided text.",
        ],
        "env_cleanup": [],
        "models": {"best": "pro", "normal": "flash"},
        "uses_stdin": True,
    },
}


class AIRouter:
    """Routes AI calls to claude/gemini with failover."""

    def __init__(self, providers=None):
        available = []
        for name in (providers or ["claude", "gemini"]):
            if name not in PROVIDERS:
                log.warning(f"Unknown AI provider: {name}")
                continue
            binary = PROVIDERS[name]["cmd_text"]("dummy")[0]
            if shutil.which(binary):
                available.append(name)
                log.info(f"AI provider available: {name}")
            else:
                log.warning(f"AI provider not found: {name} ({binary})")
        if not available:
            log.error("No AI providers available")
            sys.exit(1)
        self.available_providers = list(available)
        self.providers = list(available)

    def reset_providers(self):
        self.providers = list(self.available_providers)

    def disable_provider(self, name):
        if name in self.providers:
            self.providers.remove(name)
            log.warning(f"AI provider disabled: {name}")

    @property
    def has_providers(self):
        return len(self.providers) > 0

    def call(self, prompt, tier="best", timeout=600, allow_edits=False,
             cwd=None, provider_override=None):
        """Call an AI provider. Retries indefinitely with wait on full exhaustion.

        Returns (stdout, exit_code, provider_name).
        """
        while True:
            provider_name = provider_override or (
                random.choice(self.providers) if self.providers else None
            )

            if provider_name is None:
                log.warning("All AI providers exhausted. Waiting 5 minutes...")
                time.sleep(300)
                self.reset_providers()
                continue

            stdout, rc = self._invoke(provider_name, prompt, tier, timeout,
                                      allow_edits, cwd)

            if rc == 0:
                return stdout, rc, provider_name

            log.warning(f"AI: {provider_name} failed (rc={rc})")
            if not provider_override:
                self.disable_provider(provider_name)
            else:
                log.warning(f"Override provider {provider_name} failed. Waiting...")
                time.sleep(300)

    def _invoke(self, provider_name, prompt, tier, timeout, allow_edits, cwd):
        spec = PROVIDERS[provider_name]
        model = spec["models"][tier]

        if allow_edits:
            cmd = spec["cmd_edit"](model)
        else:
            cmd = spec["cmd_text"](model)

        env = os.environ.copy()
        for var in spec["env_cleanup"]:
            env.pop(var, None)

        log.info(f"AI: calling {provider_name}/{model} (edits={allow_edits})")

        try:
            kwargs = dict(
                capture_output=True, text=True,
                timeout=timeout, env=env,
            )
            if cwd:
                kwargs["cwd"] = cwd
            if spec["uses_stdin"]:
                kwargs["input"] = prompt
            else:
                cmd.append(prompt)

            result = subprocess.run(cmd, **kwargs)
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            log.error(f"TIMEOUT: {provider_name} exceeded {timeout}s")
            return "", 1
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_ai.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/ai.py tests/test_ai.py
git commit -m "feat: AI provider routing with failover"
```

---

### Task 10: Prompt builders

**Files:**
- Create: `tests/test_prompts.py`
- Create: `optimise/prompts.py`

- [ ] **Step 1: Write failing tests for prompt builders**

```python
# tests/test_prompts.py
import pytest
from optimise.prompts import (
    build_generation_prompt,
    build_selection_prompt,
    build_implementation_prompt,
    build_review_prompt,
)


class TestGenerationPrompt:
    def test_includes_instructions(self):
        prompt = build_generation_prompt(
            instructions="Optimise diffuse.c",
            learnings="## What works\n- inlining",
            existing_titles=["Title A"],
            count=3,
            target_files=["src/main.c"],
        )
        assert "Optimise diffuse.c" in prompt
        assert "inlining" in prompt
        assert "Title A" in prompt
        assert "3" in prompt

    def test_includes_target_files(self):
        prompt = build_generation_prompt(
            instructions="Optimise",
            learnings="",
            existing_titles=[],
            count=2,
            target_files=["src/a.c", "src/b.c"],
        )
        assert "src/a.c" in prompt
        assert "src/b.c" in prompt


class TestSelectionPrompt:
    def test_includes_all_ideas(self):
        ideas = {"idea-a.md": "Title A\n\nBody A", "idea-b.md": "Title B\n\nBody B"}
        prompt = build_selection_prompt(ideas)
        assert "idea-a.md" in prompt
        assert "Title A" in prompt
        assert "idea-b.md" in prompt


class TestImplementationPrompt:
    def test_includes_idea_and_instructions(self):
        prompt = build_implementation_prompt(
            instructions="Optimise diffuse.c",
            learnings="## What works\n- inlining",
            idea_content="Remove redundant loop\n\nDetails here",
            target_files=["src/diffuse.c"],
            errors=None,
        )
        assert "Optimise diffuse.c" in prompt
        assert "Remove redundant loop" in prompt
        assert "src/diffuse.c" in prompt

    def test_has_multiple_prohibitions(self):
        prompt = build_implementation_prompt(
            instructions="", learnings="",
            idea_content="idea",
            target_files=["f.c"],
            errors=None,
        )
        # Must have at least 3 separate prohibitions
        prohibitions = [line for line in prompt.split("\n")
                       if "MUST NOT" in line or "FORBIDDEN" in line or "PENALIZED" in line
                       or "PROHIBITED" in line or "NEVER" in line]
        assert len(prohibitions) >= 3

    def test_includes_errors_when_present(self):
        prompt = build_implementation_prompt(
            instructions="", learnings="",
            idea_content="idea",
            target_files=["f.c"],
            errors="error: undefined reference to foo",
        )
        assert "undefined reference to foo" in prompt
        assert "fix" in prompt.lower() or "Fix" in prompt


class TestReviewPrompt:
    def test_includes_done_ideas(self):
        done_ideas = {"a.md": "Title A\n\nBody\noutcome: improvement",
                      "b.md": "Title B\n\nBody\noutcome: build failure"}
        prompt = build_review_prompt(
            instructions="Optimise",
            done_ideas=done_ideas,
        )
        assert "Title A" in prompt
        assert "improvement" in prompt
        assert "build failure" in prompt
        assert "learnings.md" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_prompts.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement prompts module**

```python
# optimise/prompts.py
"""Prompt builders for each LLM role."""


def build_generation_prompt(instructions, learnings, existing_titles, count, target_files):
    """Build prompt for batch idea generation.

    The LLM should read the target files to understand the code, then propose
    `count` optimisation ideas. Each idea needs a filename, title, and description.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)
    existing = "\n".join(f"- {t}" for t in existing_titles) if existing_titles else "(none yet)"

    return f"""\
# Instructions

{instructions}

# Target files

Read these files to understand the code: {targets}

# Learnings from past experiments

{learnings}

# Existing ideas (do NOT repeat these)

{existing}

# Your task

Generate exactly {count} new optimisation ideas for the target files.

For EACH idea, output in this exact format (with the triple-dash separator between ideas):

---
FILENAME: a-brief-descriptive-name
TITLE: one line suitable as a git commit message
DESCRIPTION:
A short paragraph explaining what to change and why it should improve performance.
---

Rules:
- Filenames must use only [a-zA-Z0-9_-], no extension
- Each idea must be genuinely different from the existing ideas listed above
- Focus on ideas that are likely to succeed based on the learnings
"""


def build_selection_prompt(ideas):
    """Build prompt for selecting the best idea to try next.

    Args:
        ideas: dict of {filename: content} for all ideas in todo/
    """
    sections = []
    for filename, content in sorted(ideas.items()):
        sections.append(f"## {filename}\n\n{content}")
    ideas_text = "\n\n".join(sections)

    return f"""\
# Idea Selection

Below are the candidate optimisation ideas. Select the one most likely to
improve performance. Consider which idea has the best risk/reward ratio.

{ideas_text}

# Your task

Return ONLY the filename of the selected idea (e.g. `my-idea.md`).
Do not explain your reasoning. Just output the filename.
"""


def build_implementation_prompt(instructions, learnings, idea_content, target_files, errors):
    """Build prompt for implementing an optimisation idea.

    Contains at least three separate, strong prohibitions against running
    builds/tests/benchmarks.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)

    error_block = ""
    if errors:
        error_block = f"""
## PREVIOUS ATTEMPT FAILED

The previous attempt to implement this idea resulted in errors.
You MUST fix these errors. Here is the build/test output:

```
{errors}
```
"""

    return f"""\
# Instructions

{instructions}

# Learnings from past experiments

{learnings}

# Your task

Implement this optimisation idea by editing the target files ({targets}):

{idea_content}

{error_block}

## CRITICAL RULES — READ EVERY ONE

1. Use the Read tool to read the target files. Use Edit to make changes.
2. Make ONLY the changes described in the idea. Do not refactor other code.

3. **YOU MUST NOT RUN ANY BUILD COMMANDS. THIS IS FORBIDDEN.**
4. **YOU MUST NOT RUN ANY TEST COMMANDS. THIS IS PROHIBITED.**
5. **YOU MUST NOT RUN ANY BENCHMARK COMMANDS. YOU WILL BE PENALIZED.**
6. **YOU MUST NEVER USE SHELL/BASH TOOLS TO EXECUTE ANYTHING.**
7. **IF YOU ATTEMPT TO BUILD, TEST, OR BENCHMARK, THE SESSION WILL BE TERMINATED.**

The orchestrator script handles ALL building, testing, and benchmarking
after you return control. Your ONLY job is to edit the source files.

When done editing, output a brief summary of what you changed.
"""


def build_review_prompt(instructions, done_ideas):
    """Build prompt for periodic strategy review.

    The LLM gets Read+Edit on the script repo to update learnings.md.
    """
    sections = []
    for filename, content in sorted(done_ideas.items()):
        sections.append(f"## {filename}\n\n{content}")
    ideas_text = "\n\n".join(sections)

    return f"""\
# Instructions

{instructions}

# Completed experiments

{ideas_text}

# Your task

Review all completed experiments above. Update `learnings.md` using the
Read and Edit tools. The file should have two sections:

## What works
Bullet points describing patterns that consistently lead to successful
optimisations, with evidence from the experiments.

## What to avoid
Bullet points describing patterns that consistently fail, with reasons.

Keep it concise: 10-20 bullet points total. You may update, remove, or
add entries based on the evidence. Remove entries that are contradicted
by newer evidence.
"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/prompts.py tests/test_prompts.py
git commit -m "feat: prompt builders for all LLM roles"
```

---

### Task 11: Runner — startup recovery and state machine

**Files:**
- Create: `tests/test_runner.py`
- Create: `optimise/runner.py`

- [ ] **Step 1: Write failing tests for startup recovery**

```python
# tests/test_runner.py
import os
import subprocess
import pytest
from unittest.mock import MagicMock, patch
from optimise.runner import determine_startup_state, StartupState, run_shell_step


class TestDetermineStartupState:
    def _setup(self, tmp_path):
        """Wire up directories and return paths."""
        import subprocess
        script_repo = tmp_path / "script"
        target_repo = tmp_path / "target"
        script_repo.mkdir()
        target_repo.mkdir()
        subprocess.run(["git", "init"], cwd=target_repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=target_repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=target_repo, check=True, capture_output=True)
        (target_repo / ".gitkeep").write_text("")
        subprocess.run(["git", "add", "."], cwd=target_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=target_repo, check=True, capture_output=True)
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            (script_repo / d).mkdir(parents=True, exist_ok=True)
        return str(script_repo), str(target_repo)

    def test_empty_perf_logs_returns_baseline(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        state = determine_startup_state(sr, tr)
        assert state == StartupState.BASELINE

    def test_existing_perf_logs_returns_generate(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.GENERATE

    def test_idea_in_coding_clean_target_returns_code(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (script_repo / "ideas" / "coding" / "idea.md").write_text("Title\n\nBody")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.CODE

    def test_idea_in_coding_dirty_target_rolls_back(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (script_repo / "ideas" / "coding" / "idea.md").write_text("Title\n\nBody")
        # Make target dirty
        (git_repo / ".gitkeep").write_text("dirty")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.CODE
        # Target should be clean now
        assert (git_repo / ".gitkeep").read_text() == ""

    def test_idea_in_testing_dirty_target_returns_test(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (script_repo / "ideas" / "testing" / "idea.md").write_text("Title\n\nBody")
        # Make target dirty (meaning edits are present)
        (git_repo / ".gitkeep").write_text("dirty")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.TEST

    def test_idea_in_testing_clean_target_moves_to_coding(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (script_repo / "ideas" / "testing" / "idea.md").write_text("Title\n\nBody")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.CODE
        # Idea should have moved to coding
        assert (script_repo / "ideas" / "coding" / "idea.md").exists()
        assert not (script_repo / "ideas" / "testing" / "idea.md").exists()

    def test_multiple_ideas_in_coding_errors(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "ideas" / "coding" / "a.md").write_text("A")
        (script_repo / "ideas" / "coding" / "b.md").write_text("B")
        with pytest.raises(SystemExit):
            determine_startup_state(sr, tr)

    def test_orphan_dirty_target_rolls_back(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (git_repo / ".gitkeep").write_text("dirty")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.GENERATE
        assert (git_repo / ".gitkeep").read_text() == ""

    def test_cleans_errors_txt_on_coding_recovery(self, tmp_path):
        git_repo = tmp_path / "target"
        script_repo = tmp_path / "script"
        sr, tr = self._setup(tmp_path)
        (script_repo / "perf-logs" / "baseline-perf.md").write_text("data")
        (script_repo / "ideas" / "coding" / "idea.md").write_text("Title\n\nBody")
        (script_repo / "ideas" / "coding" / "errors.txt").write_text("old errors")
        state = determine_startup_state(sr, tr)
        assert state == StartupState.CODE
        assert not (script_repo / "ideas" / "coding" / "errors.txt").exists()


class TestRunShellStep:
    def test_success(self):
        ok, output = run_shell_step("TEST", "echo hello", cwd="/tmp")
        assert ok
        assert "hello" in output

    def test_failure(self):
        ok, output = run_shell_step("TEST", "false", cwd="/tmp")
        assert not ok
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement runner module (startup + shell step)**

```python
# optimise/runner.py
"""Main orchestration loop — state machine for the optimisation process."""
import enum
import logging
import os
import subprocess
import sys
import time

from optimise.git import GitRepo
from optimise.state import list_ideas, move_idea, clean_errors

log = logging.getLogger("optimiser")


class StartupState(enum.Enum):
    BASELINE = "baseline"
    GENERATE = "generate"
    CODE = "code"
    TEST = "test"


def determine_startup_state(script_repo, target_repo_path):
    """Determine what state to resume from on startup.

    Implements the recovery-aware startup logic from the spec.
    Returns a StartupState enum.
    """
    target = GitRepo(target_repo_path)

    # Check for multiple files in coding/testing
    for subdir in ("coding", "testing"):
        files = list_ideas(script_repo, subdir)
        if len(files) > 1:
            log.error(
                f"Unexpected state: multiple files in ideas/{subdir}/: {files}. "
                f"Please investigate."
            )
            sys.exit(1)

    # Check ideas/testing/
    testing_files = list_ideas(script_repo, "testing")
    if testing_files:
        if target.is_dirty():
            log.info("Resuming: idea in testing/, target dirty → TEST")
            return StartupState.TEST
        else:
            log.info("Resuming: idea in testing/, target clean → moving to coding/, CODE")
            move_idea(script_repo, testing_files[0], "testing", "coding")
            clean_errors(script_repo)
            return StartupState.CODE

    # Check ideas/coding/
    coding_files = list_ideas(script_repo, "coding")
    if coding_files:
        if target.is_dirty():
            log.info("Resuming: idea in coding/, target dirty → rollback, CODE")
            target.rollback()
        else:
            log.info("Resuming: idea in coding/, target clean → CODE")
        clean_errors(script_repo)
        return StartupState.CODE

    # Orphan dirty state
    if target.is_dirty():
        log.info("Orphan dirty state in target repo — rolling back")
        target.rollback()

    # Check if baseline exists
    perf_dir = os.path.join(script_repo, "perf-logs")
    if not os.path.isdir(perf_dir) or not os.listdir(perf_dir):
        return StartupState.BASELINE

    return StartupState.GENERATE


def run_shell_step(name, cmd_str, cwd):
    """Run a shell command. Returns (success: bool, output: str)."""
    log.info(f"{name}: running `{cmd_str[:80]}`...")
    result = subprocess.run(
        cmd_str, shell=True,
        capture_output=True, text=True, timeout=600, cwd=cwd,
    )
    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += result.stderr

    if result.returncode != 0:
        log.error(f"{name}: FAILED (rc={result.returncode})")
        return False, output

    log.info(f"{name}: OK")
    return True, output
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/runner.py tests/test_runner.py
git commit -m "feat: runner startup recovery and shell step"
```

---

### Task 12: CLI — init command

**Files:**
- Create: `tests/test_cli.py`
- Create: `optimise/cli.py`
- Modify: `optimise.py`

- [ ] **Step 1: Write failing tests for init**

```python
# tests/test_cli.py
import os
import pytest
from optimise.cli import do_init


class TestInit:
    def test_creates_settings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").exists()
        content = (tmp_path / "settings.conf").read_text()
        assert "target_repo:" in content
        assert "build_cmd:" in content

    def test_creates_instructions(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "instructions.md").exists()

    def test_creates_learnings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "learnings.md").exists()
        content = (tmp_path / "learnings.md").read_text()
        assert "## What works" in content
        assert "## What to avoid" in content

    def test_creates_directories(self, tmp_path):
        do_init(str(tmp_path))
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            assert (tmp_path / d).is_dir()

    def test_idempotent_does_not_overwrite(self, tmp_path):
        do_init(str(tmp_path))
        # Modify settings
        (tmp_path / "settings.conf").write_text("custom content")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom content"

    def test_creates_missing_files_only(self, tmp_path):
        # Create settings but not learnings
        (tmp_path / "settings.conf").write_text("custom")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom"
        assert (tmp_path / "learnings.md").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement CLI module and update entry point**

```python
# optimise/cli.py
"""CLI commands: init and run."""
import os
import logging

from optimise.settings import SETTINGS_TEMPLATE, INSTRUCTIONS_TEMPLATE, LEARNINGS_TEMPLATE

log = logging.getLogger("optimiser")


def do_init(directory):
    """Scaffold a new optimiser script repo.

    Creates settings.conf, instructions.md, learnings.md, and the
    ideas/ and perf-logs/ directory structure. Does not overwrite
    existing files.
    """
    files = {
        "settings.conf": SETTINGS_TEMPLATE,
        "instructions.md": INSTRUCTIONS_TEMPLATE,
        "learnings.md": LEARNINGS_TEMPLATE,
    }

    for filename, content in files.items():
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            log.info(f"  exists, skipping: {filename}")
        else:
            with open(path, "w") as f:
                f.write(content)
            log.info(f"  created: {filename}")

    dirs = [
        "ideas/todo",
        "ideas/coding",
        "ideas/testing",
        "ideas/done",
        "perf-logs",
    ]
    for d in dirs:
        path = os.path.join(directory, d)
        os.makedirs(path, exist_ok=True)
        log.info(f"  directory: {d}/")
```

Update `optimise.py`:

```python
#!/usr/bin/env python3
"""Optimiser — automated performance optimisation via LLM."""
import argparse
import logging
import os
import sys

from optimise.cli import do_init


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Automated performance optimisation via LLM",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold a new optimiser workspace")
    init_parser.add_argument("--dir", default=".",
                            help="Directory to scaffold (default: current)")

    # run command
    run_parser = subparsers.add_parser("run", help="Run the optimisation loop")
    run_parser.add_argument("--dir", default=".",
                           help="Script repo directory (default: current)")

    args = parser.parse_args()

    if args.command == "init":
        directory = os.path.abspath(args.dir)
        print(f"Initialising optimiser workspace in {directory}")
        do_init(directory)
        print("Done. Edit settings.conf and instructions.md, then run: python optimise.py run")
    elif args.command == "run":
        print("Run command not yet implemented.")
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_cli.py -v`
Expected: All PASS

- [ ] **Step 5: Verify init command works end-to-end**

Run: `cd /tmp && python /workspace/optimiser/optimise.py init --dir /tmp/test-optimiser && ls -la /tmp/test-optimiser/`
Expected: settings.conf, instructions.md, learnings.md, ideas/, perf-logs/ all present

- [ ] **Step 6: Commit**

```bash
git add optimise/cli.py optimise.py tests/test_cli.py
git commit -m "feat: init command and CLI entry point"
```

---

### Task 13: Runner — main orchestration loop

**Files:**
- Modify: `tests/test_runner.py`
- Modify: `optimise/runner.py`
- Modify: `optimise/cli.py`

This is the integration task that wires everything together. Tests use mocks
for the AI module (no real LLM calls) but real filesystem and git operations.

- [ ] **Step 1: Write failing tests for termination conditions**

Append to `tests/test_runner.py`:

```python
from optimise.runner import check_termination, TerminationReason


class TestCheckTermination:
    def test_max_iterations(self):
        reason = check_termination(
            iteration=50, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.MAX_ITERATIONS

    def test_stagnation(self):
        reason = check_termination(
            iteration=10, max_iterations=50,
            consecutive_perf_failures=5, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.STAGNATION

    def test_time_limit(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time() - 400 * 60, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.TIME_LIMIT

    def test_no_termination(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time(), max_minutes=300, todo_count=5,
        )
        assert reason is None

    def test_idea_exhaustion(self):
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=0,
        )
        assert reason == TerminationReason.IDEA_EXHAUSTION
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py::TestCheckTermination -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement termination checking**

Append to `optimise/runner.py`:

```python
class TerminationReason(enum.Enum):
    MAX_ITERATIONS = "max iterations reached"
    STAGNATION = "no performance improvement"
    IDEA_EXHAUSTION = "cannot generate new ideas"
    TIME_LIMIT = "time limit exceeded"


def check_termination(iteration, max_iterations, consecutive_perf_failures,
                      max_consecutive, start_time, max_minutes, todo_count):
    """Check if any termination condition is met.

    Returns a TerminationReason or None.
    """
    if todo_count == 0:
        return TerminationReason.IDEA_EXHAUSTION
    if iteration >= max_iterations:
        return TerminationReason.MAX_ITERATIONS
    if consecutive_perf_failures >= max_consecutive:
        return TerminationReason.STAGNATION
    elapsed_minutes = (time.time() - start_time) / 60
    if elapsed_minutes >= max_minutes:
        return TerminationReason.TIME_LIMIT
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/runner.py tests/test_runner.py
git commit -m "feat: termination condition checking"
```

---

### Task 14: Runner — benchmark orchestration (convergence loop wrapper)

**Files:**
- Modify: `tests/test_runner.py`
- Modify: `optimise/runner.py`

- [ ] **Step 1: Write failing tests for benchmark orchestration**

Append to `tests/test_runner.py`:

```python
from optimise.runner import run_benchmark_loop
from optimise.benchmark import BenchmarkError


class TestRunBenchmarkLoop:
    def _make_bench_script(self, tmp_path, outputs):
        """Create a script that outputs different values each call."""
        script = tmp_path / "bench.sh"
        state_file = tmp_path / "call_count"
        state_file.write_text("0")
        # Write all outputs to separate files
        for i, output in enumerate(outputs):
            (tmp_path / f"output_{i}.txt").write_text(output)
        script.write_text(f"""\
#!/bin/bash
COUNT=$(cat {state_file})
cat {tmp_path}/output_$COUNT.txt
echo $((COUNT + 1)) > {state_file}
""")
        script.chmod(0o755)
        return str(script)

    def test_single_run_converges(self, tmp_path):
        # All runs return same value → converges after tail_runs
        outputs = ["user=1.000\n"] * 7
        cmd = self._make_bench_script(tmp_path, outputs)
        result = run_benchmark_loop(
            bench_cmd=cmd, cwd=str(tmp_path),
            baseline_user_sum=2.0,
            num_warmup=0,
            convergence_threshold_pct=0.1,
            convergence_tail_runs=3,
            early_abort_regression_pct=10,
        )
        assert result is not None
        assert len(result) == 1
        assert result[0]["user"] == pytest.approx(1.0)

    def test_early_abort_on_regression(self, tmp_path):
        outputs = ["user=3.000\n"]  # > 10% worse than baseline of 2.0
        cmd = self._make_bench_script(tmp_path, outputs)
        with pytest.raises(BenchmarkError, match="early abort"):
            run_benchmark_loop(
                bench_cmd=cmd, cwd=str(tmp_path),
                baseline_user_sum=2.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_regression_pct=10,
            )

    def test_warmup_runs_are_skipped(self, tmp_path):
        # First output is bad (would trigger early abort), but it's warmup
        outputs = [
            "user=999.000\n",  # warmup — discarded
            "user=1.000\n",    # first real run
            "user=1.000\n",
            "user=1.000\n",
            "user=1.000\n",
        ]
        cmd = self._make_bench_script(tmp_path, outputs)
        result = run_benchmark_loop(
            bench_cmd=cmd, cwd=str(tmp_path),
            baseline_user_sum=2.0,
            num_warmup=1,
            convergence_threshold_pct=0.1,
            convergence_tail_runs=3,
            early_abort_regression_pct=10,
        )
        assert result[0]["user"] == pytest.approx(1.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py::TestRunBenchmarkLoop -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement benchmark loop**

Append to `optimise/runner.py`:

```python
from optimise.benchmark import (
    parse_bench_output, update_element_best, sum_user,
    ConvergenceState, BenchmarkError,
)


def run_benchmark_loop(bench_cmd, cwd, baseline_user_sum,
                       num_warmup, convergence_threshold_pct,
                       convergence_tail_runs, early_abort_regression_pct):
    """Run the benchmark convergence loop.

    Returns element-wise best rows on success.
    Raises BenchmarkError on early abort or parse failure.
    """
    # Warmup
    for i in range(num_warmup):
        log.info(f"BENCH warmup {i+1}/{num_warmup}")
        subprocess.run(
            bench_cmd, shell=True,
            capture_output=True, text=True, timeout=600, cwd=cwd,
        )

    best = None
    convergence = ConvergenceState(convergence_threshold_pct, convergence_tail_runs)
    run_idx = 0

    while True:
        run_idx += 1
        log.info(f"BENCH run {run_idx}")

        result = subprocess.run(
            bench_cmd, shell=True,
            capture_output=True, text=True, timeout=600, cwd=cwd,
        )
        rows = parse_bench_output(result.stdout)
        best = update_element_best(best, rows)
        current_sum = sum_user(best)

        # Early abort on first real run
        if run_idx == 1:
            threshold = baseline_user_sum * (1 + early_abort_regression_pct / 100)
            if current_sum > threshold:
                raise BenchmarkError(
                    f"Benchmark early abort: {current_sum:.3f}s > "
                    f"{threshold:.3f}s ({early_abort_regression_pct}% worse than baseline)"
                )

        convergence.update(current_sum)
        log.info(f"BENCH run {run_idx}: sum(user)={current_sum:.3f}s "
                 f"(tail={convergence.tail_counter}/{convergence_tail_runs})")

        if convergence.converged:
            log.info(f"BENCH converged after {run_idx} runs")
            break

    return best
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/runner.py tests/test_runner.py
git commit -m "feat: benchmark convergence loop"
```

---

### Task 15: Runner — LLM output parsers for idea generation and selection

**Files:**
- Modify: `tests/test_runner.py`
- Modify: `optimise/runner.py`

- [ ] **Step 1: Write failing tests for parsing LLM output**

Append to `tests/test_runner.py`:

```python
from optimise.runner import parse_generated_ideas, parse_selection


class TestParseGeneratedIdeas:
    def test_parses_structured_output(self):
        text = """
---
FILENAME: precompute-half-aniso
TITLE: precompute half_anisotropy outside pixel loop
DESCRIPTION:
Move the computation of half_anisotropy outside the inner loop
to save 4 multiplies per pixel.
---
---
FILENAME: unroll-gradient-calc
TITLE: unroll gradient calculation loop
DESCRIPTION:
Replace the for loop with explicit scalar operations.
---
"""
        ideas = parse_generated_ideas(text)
        assert len(ideas) == 2
        assert ideas[0]["filename"] == "precompute-half-aniso"
        assert ideas[0]["title"] == "precompute half_anisotropy outside pixel loop"
        assert "half_anisotropy" in ideas[0]["description"]
        assert ideas[1]["filename"] == "unroll-gradient-calc"

    def test_empty_output(self):
        ideas = parse_generated_ideas("")
        assert ideas == []


class TestParseSelection:
    def test_extracts_filename(self):
        assert parse_selection("idea-a.md\n") == "idea-a.md"

    def test_extracts_from_backticks(self):
        assert parse_selection("The best idea is `idea-b.md`") == "idea-b.md"

    def test_strips_whitespace(self):
        assert parse_selection("  idea-c.md  \n") == "idea-c.md"

    def test_returns_none_on_garbage(self):
        assert parse_selection("I think we should try something") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py::TestParseGeneratedIdeas tests/test_runner.py::TestParseSelection -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement parsers**

Append to `optimise/runner.py`:

```python
import re


def parse_generated_ideas(text):
    """Parse LLM output into a list of idea dicts.

    Expected format: blocks delimited by --- with FILENAME:, TITLE:, DESCRIPTION: fields.
    Returns list of {"filename": str, "title": str, "description": str}.
    """
    ideas = []
    blocks = re.split(r"^---\s*$", text.strip(), flags=re.MULTILINE)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        fname_m = re.search(r"FILENAME:\s*(.+)", block)
        title_m = re.search(r"TITLE:\s*(.+)", block)
        desc_m = re.search(r"DESCRIPTION:\s*\n?([\s\S]*?)$", block)

        if fname_m and title_m:
            ideas.append({
                "filename": fname_m.group(1).strip(),
                "title": title_m.group(1).strip(),
                "description": desc_m.group(1).strip() if desc_m else "",
            })

    return ideas


def parse_selection(text):
    """Parse LLM selection output to extract a filename.

    Looks for a .md filename in the output. Returns the filename or None.
    """
    text = text.strip()
    # Try backtick-wrapped
    m = re.search(r"`([a-zA-Z0-9_\-]+\.md)`", text)
    if m:
        return m.group(1)
    # Try bare filename
    m = re.search(r"([a-zA-Z0-9_\-]+\.md)", text)
    if m:
        return m.group(1)
    # Try just the text if it looks like a filename
    if re.match(r"^[a-zA-Z0-9_\-]+\.md$", text):
        return text
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /workspace/optimiser && python -m pytest tests/test_runner.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/runner.py tests/test_runner.py
git commit -m "feat: LLM output parsers for idea generation and selection"
```

---

### Task 16: Wire up the `run` command

**Files:**
- Modify: `optimise/cli.py`
- Modify: `optimise/runner.py`
- Modify: `optimise.py`

This task connects everything into the main loop. The full loop is too
complex to unit test in isolation — it will be validated via integration
testing with mock LLM responses.

- [ ] **Step 1: Implement the `do_run` function in cli.py**

Append to `optimise/cli.py`:

```python
import sys
import time

from optimise.settings import parse_settings, validate_settings, SettingsError
from optimise.git import GitRepo, GitError
from optimise.ai import AIRouter
from optimise.runner import (
    determine_startup_state, StartupState, TerminationReason,
    check_termination, run_shell_step, run_benchmark_loop,
    parse_generated_ideas, parse_selection,
)
from optimise.state import (
    list_ideas, move_idea, read_idea, create_idea, append_outcome,
    all_idea_titles, dedup_title, clean_errors, sanitise_filename,
)
from optimise.benchmark import (
    format_perf_log, parse_perf_log, evaluate_success, sum_user, BenchmarkError,
)
from optimise.prompts import (
    build_generation_prompt, build_selection_prompt,
    build_implementation_prompt, build_review_prompt,
)


def do_run(directory):
    """Run the main optimisation loop."""
    directory = os.path.abspath(directory)

    # Load and validate settings
    settings_path = os.path.join(directory, "settings.conf")
    try:
        raw = parse_settings(settings_path)
        settings = validate_settings(raw, script_repo=directory)
    except (FileNotFoundError, SettingsError) as e:
        log.error(f"Settings error: {e}")
        sys.exit(1)

    target_repo_path = settings["target_repo"]
    target_files = settings["optimisation_target"]
    if isinstance(target_files, str):
        target_files = [target_files]

    # Branch resolution
    try:
        target_git = GitRepo(target_repo_path)
        script_git = GitRepo(directory)
        target_git.resolve_branch(settings["branch"])
        script_git.resolve_branch(settings["branch"])
    except GitError as e:
        log.error(str(e))
        sys.exit(1)

    # AI router
    ai = AIRouter()

    # Startup recovery
    startup = determine_startup_state(directory, target_repo_path)
    log.info(f"Startup state: {startup.value}")

    # Read instructions and learnings
    with open(settings["instructions"]) as f:
        instructions = f.read()

    start_time = time.time()
    iteration = 0
    consecutive_perf_failures = 0
    retries_left = settings["max_retries"]

    # State machine
    state = startup

    while True:
        ai.reset_providers()

        if state == StartupState.BASELINE:
            log.info("=== BASELINE ===")

            # Build
            ok, output = run_shell_step("BUILD", settings["build_cmd"], cwd=target_repo_path)
            if not ok:
                log.error("Baseline build failed. Cannot proceed.")
                sys.exit(1)

            # Quality check
            if settings["quality_cmd"]:
                ok, output = run_shell_step("QUALITY", settings["quality_cmd"],
                                           cwd=target_repo_path)
                if not ok:
                    log.error("Baseline quality check failed. Cannot proceed.")
                    sys.exit(1)

            # Benchmark
            try:
                best = run_benchmark_loop(
                    settings["bench_cmd"], cwd=target_repo_path,
                    baseline_user_sum=float("inf"),  # no early abort for baseline
                    num_warmup=settings["num_warmup_iterations"],
                    convergence_threshold_pct=settings["benchmark_convergence_threshold_pct"],
                    convergence_tail_runs=settings["benchmark_convergence_tail_runs"],
                    early_abort_regression_pct=settings["early_abort_regression_pct"],
                )
            except BenchmarkError as e:
                log.error(f"Baseline benchmark failed: {e}")
                sys.exit(1)

            # Save perf logs
            perf_text = format_perf_log(best)
            baseline_path = os.path.join(directory, "perf-logs", "baseline-perf.md")
            current_path = os.path.join(directory, "perf-logs", "current-best-perf.md")
            with open(baseline_path, "w") as f:
                f.write(perf_text)
            with open(current_path, "w") as f:
                f.write(perf_text)

            script_git.commit_all(f"{settings['commit_prefix']}: established baseline")
            log.info(f"Baseline established: sum(user)={sum_user(best):.3f}s")
            state = StartupState.GENERATE
            continue

        if state == StartupState.GENERATE:
            # Top up ideas
            todo_count = len(list_ideas(directory, "todo"))
            needed = settings["min_ideas"] - todo_count

            if needed > 0:
                learnings = _read_learnings(directory)
                existing_titles = all_idea_titles(directory)
                attempts = 0

                while needed > 0 and attempts < settings["max_dedup_attempts"]:
                    attempts += 1
                    prompt = build_generation_prompt(
                        instructions, learnings, existing_titles, needed, target_files,
                    )
                    output, rc, provider = ai.call(
                        prompt, tier="best", cwd=target_repo_path,
                    )
                    if rc != 0:
                        log.warning(f"Idea generation failed ({provider})")
                        continue

                    ideas = parse_generated_ideas(output)
                    added = 0
                    for idea in ideas:
                        if dedup_title(idea["title"], existing_titles):
                            log.info(f"Dedup: skipping duplicate idea: {idea['title'][:60]}")
                            continue
                        content = f"{idea['title']}\n\n{idea['description']}"
                        create_idea(directory, idea["filename"], content)
                        existing_titles.append(idea["title"])
                        added += 1

                    if added > 0:
                        script_git.commit_all(f"generated {added} new ideas")
                    needed = settings["min_ideas"] - len(list_ideas(directory, "todo"))

            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
                len(list_ideas(directory, "todo"))
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

            # Select
            todo_files = list_ideas(directory, "todo")
            ideas_dict = {}
            for f in todo_files:
                path = os.path.join(directory, "ideas", "todo", f)
                with open(path) as fh:
                    ideas_dict[f] = fh.read()

            prompt = build_selection_prompt(ideas_dict)
            selected = None
            for attempt in range(4):  # 1 initial + 3 retries
                output, rc, provider = ai.call(
                    prompt, tier="best", cwd=target_repo_path,
                )
                if rc == 0:
                    selected = parse_selection(output)
                    if selected and selected in todo_files:
                        break
                    log.warning(f"Invalid selection: {output[:60]}")
                    selected = None

            if not selected:
                selected = todo_files[0]
                log.warning(f"Falling back to first idea: {selected}")

            move_idea(directory, selected, "todo", "coding")
            log.info(f"Selected idea: {selected}")
            retries_left = settings["max_retries"]
            state = StartupState.CODE
            continue

        if state == StartupState.CODE:
            iteration += 1
            coding_files = list_ideas(directory, "coding")
            idea_file = coding_files[0]
            idea_title, idea_body = read_idea(directory, "coding", idea_file)

            learnings = _read_learnings(directory)
            idea_content = f"{idea_title}\n\n{idea_body}"

            # Check for errors from previous attempt
            errors_path = os.path.join(directory, "ideas", "coding", "errors.txt")
            errors = None
            if os.path.exists(errors_path):
                with open(errors_path) as f:
                    errors = f.read()

            prompt = build_implementation_prompt(
                instructions, learnings, idea_content, target_files, errors,
            )
            log.info(f"AI: implementing idea: {idea_title[:80]}")
            output, rc, provider = ai.call(
                prompt, tier="best", cwd=target_repo_path, allow_edits=True,
            )

            if rc != 0:
                log.error(f"AI implementation failed ({provider})")
                retries_left -= 1
                if retries_left <= 0:
                    state_obj = _BuildState(directory, target_repo_path, target_git,
                                       script_git, settings, idea_file, iteration,
                                       consecutive_perf_failures, start_time)
                    state_result = _fail_idea(state_obj, "AI implementation failed")
                    consecutive_perf_failures = state_result["consecutive_perf_failures"]
                    state = StartupState.GENERATE
                else:
                    state = StartupState.CODE
                continue

            state = _BuildState(directory, target_repo_path, target_git,
                               script_git, settings, idea_file, iteration,
                               consecutive_perf_failures, start_time)
            # Fall through to BUILD
            state_result = _do_build_test_benchmark(state, retries_left)
            consecutive_perf_failures = state_result["consecutive_perf_failures"]
            retries_left = state_result.get("retries_left", retries_left)

            if state_result.get("retry_code"):
                state = StartupState.CODE
                continue

            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
                len(list_ideas(directory, "todo"))
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

            # Check review
            if iteration % settings["review_frequency"] == 0:
                _do_review(directory, script_git, ai, instructions, target_repo_path)

            state = StartupState.GENERATE
            continue

        if state == StartupState.TEST:
            coding_or_testing = "testing"
            files = list_ideas(directory, coding_or_testing)
            idea_file = files[0]

            state_obj = _BuildState(directory, target_repo_path, target_git,
                                   script_git, settings, idea_file, iteration,
                                   consecutive_perf_failures, start_time,
                                   skip_build=True)
            state_result = _do_build_test_benchmark(state_obj, retries_left)
            consecutive_perf_failures = state_result["consecutive_perf_failures"]
            retries_left = state_result.get("retries_left", retries_left)

            if state_result.get("retry_code"):
                state = StartupState.CODE
                continue

            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
                len(list_ideas(directory, "todo"))
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

            if iteration % settings["review_frequency"] == 0:
                _do_review(directory, script_git, ai, instructions, target_repo_path)

            state = StartupState.GENERATE
            continue


class _BuildState:
    """Bundle of state for the build→test→benchmark pipeline."""
    def __init__(self, script_repo, target_repo_path, target_git, script_git,
                 settings, idea_file, iteration, consecutive_perf_failures,
                 start_time, skip_build=False):
        self.script_repo = script_repo
        self.target_repo_path = target_repo_path
        self.target_git = target_git
        self.script_git = script_git
        self.settings = settings
        self.idea_file = idea_file
        self.iteration = iteration
        self.consecutive_perf_failures = consecutive_perf_failures
        self.start_time = start_time
        self.skip_build = skip_build


def _do_build_test_benchmark(s, retries_left):
    """Run the BUILD→TEST→BENCHMARK pipeline.

    Returns dict with "consecutive_perf_failures" and optional "retry_code".
    """
    idea_subdir = "testing" if s.skip_build else "coding"

    # BUILD
    if not s.skip_build:
        ok, output = run_shell_step("BUILD", s.settings["build_cmd"],
                                    cwd=s.target_repo_path)
        if not ok:
            errors_path = os.path.join(s.script_repo, "ideas", "coding", "errors.txt")
            with open(errors_path, "w") as f:
                f.write(output)
            retries_left -= 1
            if retries_left > 0:
                return {"consecutive_perf_failures": s.consecutive_perf_failures,
                        "retry_code": True, "retries_left": retries_left}
            # Exhausted
            return _fail_idea(s, "build failure")

        # Move to testing
        move_idea(s.script_repo, s.idea_file, "coding", "testing")
        idea_subdir = "testing"

    # TEST
    if s.settings["quality_cmd"]:
        ok, output = run_shell_step("QUALITY", s.settings["quality_cmd"],
                                    cwd=s.target_repo_path)
        if not ok:
            move_idea(s.script_repo, s.idea_file, "testing", "coding")
            errors_path = os.path.join(s.script_repo, "ideas", "coding", "errors.txt")
            with open(errors_path, "w") as f:
                f.write(output)
            retries_left -= 1
            if retries_left > 0:
                return {"consecutive_perf_failures": s.consecutive_perf_failures,
                        "retry_code": True, "retries_left": retries_left}
            return _fail_idea(s, "quality regression")

    # BENCHMARK
    current_best_path = os.path.join(s.script_repo, "perf-logs", "current-best-perf.md")
    with open(current_best_path) as f:
        baseline_rows = parse_perf_log(f.read())
    baseline_sum = sum_user(baseline_rows)

    try:
        best = run_benchmark_loop(
            s.settings["bench_cmd"], cwd=s.target_repo_path,
            baseline_user_sum=baseline_sum,
            num_warmup=s.settings["num_warmup_iterations"],
            convergence_threshold_pct=s.settings["benchmark_convergence_threshold_pct"],
            convergence_tail_runs=s.settings["benchmark_convergence_tail_runs"],
            early_abort_regression_pct=s.settings["early_abort_regression_pct"],
        )
    except BenchmarkError as e:
        log.error(f"Benchmark error: {e}")
        return _fail_idea(s, "benchmark error")

    # Evaluate
    ok, improvement_pct, detail = evaluate_success(
        baseline_rows, best,
        s.settings["min_improvement_pct"],
        s.settings["individual_regression_tradeoff"],
    )

    # Save perf log for this idea
    idea_stem = s.idea_file.rsplit(".", 1)[0]
    perf_path = os.path.join(s.script_repo, "perf-logs", f"{idea_stem}-perf.md")
    with open(perf_path, "w") as f:
        f.write(format_perf_log(best))

    if ok:
        return _succeed_idea(s, best, improvement_pct, detail, baseline_sum)
    else:
        log.info(f"FAILED: {detail}")
        return _fail_idea(s, "performance regression", perf_saved=True)


def _succeed_idea(s, best, improvement_pct, detail, baseline_sum):
    """Handle a successful optimisation."""
    idea_title, idea_body = read_idea(s.script_repo, "testing", s.idea_file)
    prefix = s.settings["commit_prefix"]
    result_sum = sum_user(best)

    perf_line = (
        f"Reduced sum(user) from {baseline_sum:.3f}s to {result_sum:.3f}s "
        f"(~{improvement_pct:.1f}% improvement)"
    )
    commit_title = f"{prefix}: {idea_title}"
    commit_body = idea_body
    if commit_body:
        commit_body += f"\n\n{perf_line}"
    else:
        commit_body = perf_line

    # Commit target repo
    s.target_git.commit_all(f"{commit_title}\n\n{commit_body}")
    commit_hash = s.target_git.get_commit_hash()
    log.info(f"SUCCESS: {perf_line} (commit {commit_hash})")

    # Move idea to done
    move_idea(s.script_repo, s.idea_file, "testing", "done")
    append_outcome(s.script_repo, s.idea_file, "improvement",
                   commit_hash=commit_hash, perf_summary=perf_line)

    # Update current best
    current_best_path = os.path.join(s.script_repo, "perf-logs", "current-best-perf.md")
    with open(current_best_path, "w") as f:
        f.write(format_perf_log(best))

    s.script_git.commit_all(f"idea succeeded: {idea_title[:60]}")

    return {"consecutive_perf_failures": 0}


def _fail_idea(s, outcome, perf_saved=False):
    """Handle a failed idea."""
    # Determine which directory the idea is currently in
    for subdir in ("testing", "coding"):
        if list_ideas(s.script_repo, subdir) and \
           s.idea_file in list_ideas(s.script_repo, subdir):
            move_idea(s.script_repo, s.idea_file, subdir, "done")
            break

    append_outcome(s.script_repo, s.idea_file, outcome)
    s.target_git.rollback()
    clean_errors(s.script_repo)

    idea_title, _ = read_idea(s.script_repo, "done", s.idea_file)
    s.script_git.commit_all(f"idea failed ({outcome}): {idea_title[:60]}")

    cpf = s.consecutive_perf_failures
    if outcome == "performance regression":
        cpf += 1

    return {"consecutive_perf_failures": cpf}


def _do_review(directory, script_git, ai, instructions, target_repo_path):
    """Run the periodic strategy review."""
    log.info("=== STRATEGY REVIEW ===")
    script_git.commit_all("pre-review checkpoint")

    done_files = list_ideas(directory, "done")
    done_ideas = {}
    for f in done_files:
        path = os.path.join(directory, "ideas", "done", f)
        with open(path) as fh:
            done_ideas[f] = fh.read()

    prompt = build_review_prompt(instructions, done_ideas)
    output, rc, provider = ai.call(
        prompt, tier="best", cwd=directory, allow_edits=True,
    )
    if rc == 0:
        log.info(f"Review completed ({provider})")
    else:
        log.warning(f"Review failed ({provider})")

    script_git.commit_all("updated learnings")


def _read_learnings(directory):
    """Read learnings.md content."""
    path = os.path.join(directory, "learnings.md")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""
```

- [ ] **Step 2: Update entry point to wire up `run`**

In `optimise.py`, replace the run command handler:

```python
    elif args.command == "run":
        from optimise.cli import do_run
        do_run(args.dir)
```

- [ ] **Step 3: Run all tests**

Run: `cd /workspace/optimiser && python -m pytest -v`
Expected: All PASS

- [ ] **Step 4: Verify init + run smoke test**

Run:
```bash
cd /tmp && rm -rf test-optimiser
python /workspace/optimiser/optimise.py init --dir /tmp/test-optimiser
python /workspace/optimiser/optimise.py run --dir /tmp/test-optimiser 2>&1 | head -5
```
Expected: Settings error (target_repo not configured) — this confirms the validation pipeline works.

- [ ] **Step 5: Commit**

```bash
git add optimise/cli.py optimise/runner.py optimise.py
git commit -m "feat: wire up run command with full main loop"
```

---
