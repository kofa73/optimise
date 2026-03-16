# Optimiser — Design Specification

A configurable Python tool that drives an automated optimisation loop: generate ideas, implement via LLM, build, test, benchmark, commit or rollback. It operates across two git repositories and maintains structured state as files.

## Core Principle

Scripted execution for ALL deterministic steps (execution, state management, file operations, parsing, statistics). LLM use is restricted to natural language generation, code evaluation, and code editing. All calculations (statistics, percentages, comparisons) MUST be done in Python. No LLM "mental maths".

---

## 1. Two-Repository Architecture

The optimisation process uses two separate git repos:

- **Target repo**: the codebase being optimised. Only accumulates successful commits. Rolled back after failures via `git checkout HEAD -- .` followed by `git clean -fd` (to also remove any files the LLM may have created).
- **Script repo**: contains the optimiser tool, its configuration, state, performance data, ideas, and learnings.

This separation ensures:
- Script repo state can always be committed freely.
- Target repo only contains successful optimisation commits — clean history for pull/merge requests.
- Target repo can be rolled back to a known-good state after any failure.

### Branch Management

Both repos MUST use the same branch name, configured in settings as `branch`.

**Startup branch resolution** (applied to each repo independently):

```
current = current branch
target = configured branch name

if current == target:
    OK, proceed

else if current == default branch (main/master):
    if repo is dirty:
        inform user: "repo X has uncommitted changes on <default>, clean up first"
        exit
    if target branch does not exist:
        create target branch from current HEAD
    switch to target branch

else:
    inform user: "repo X is on branch <current>, expected <target> or <default>, clean up first"
    exit
```

Default branch detection: `git symbolic-ref refs/remotes/origin/HEAD`, with fallback to checking local `main`/`master`.

---

## 2. Project Structure

### Tool (in the script repo or installed separately)

```
optimiser/
├── optimise.py              # Entry point (thin: parse args, call cli)
├── optimise/
│   ├── __init__.py
│   ├── cli.py               # init + run commands
│   ├── settings.py          # Config parsing, validation, defaults
│   ├── state.py             # Idea lifecycle (create, move, list), file ops
│   ├── ai.py                # AIRouter — claude/gemini failover
│   ├── benchmark.py         # Convergence loop, perf output parsing, stats
│   ├── git.py               # Two-repo git operations
│   ├── prompts.py           # Prompt builders for each LLM step
│   └── runner.py            # Main orchestration loop (state machine)
└── tests/
    ├── conftest.py
    ├── test_ai.py
    ├── test_benchmark.py
    ├── test_cli.py
    ├── test_git.py
    ├── test_prompts.py
    ├── test_runner.py
    ├── test_settings.py
    └── test_state.py
```

### Script Repo (scaffolded by `init`)

```
<script-repo>/
├── settings.conf
├── instructions.md          # User-authored, passed verbatim to LLM
├── learnings.md             # LLM-edited, committed by script
├── ideas/
│   ├── todo/
│   ├── coding/
│   ├── testing/
│   └── done/
└── perf-logs/
```

---

## 3. Settings File

Created by `python optimise.py init`. Format: flat `key: value` (no YAML dependency). Lines starting with `#` are comments. The `init` command populates defaults for numeric values and instructional placeholders for user-configured values.

```
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

# === Git ===
# Commit message prefix for target repo commits.
commit_prefix: perf

# Only commit changed files under these path prefixes (comma-separated).
# Prevents accidentally committing unrelated WIP changes in the target repo.
commit_scope: src/
```

### The `init` Command

`python optimise.py init` scaffolds a new script repo working directory:

1. Creates `settings.conf` with defaults and instructional placeholders (as shown above).
2. Creates `instructions.md` with a template prompting the user to describe the optimisation task.
3. Creates `learnings.md` with empty `## What works` and `## What to avoid` sections.
4. Creates directories: `ideas/todo/`, `ideas/coding/`, `ideas/testing/`, `ideas/done/`, `perf-logs/`.
5. Does NOT overwrite existing files — if any of the above already exist, they are left untouched and a message is printed.

Running `init` in a directory that is already fully scaffolded is safe (idempotent — it only creates what is missing).

### Validation

On startup, the script validates all settings:
- Required paths exist (target_repo, optimisation_target files, instructions file).
- Required commands are non-empty (build_cmd, bench_cmd).
- Numeric values are valid.
- Actionable error messages tell the user exactly what to fix.

---

## 4. Idea Lifecycle

### Idea File Format

Each idea is a single markdown file.

**Filename:** LLM generates a brief descriptive name (no extension). The script:
1. Strips any extension the LLM may have added.
2. Replaces any character not matching `[a-zA-Z0-9_-]` with `_`.
3. Appends `.md`.

**Content (as generated):**

```markdown
remove 0.5f scaling from gradient/laplacian, absorb into half_anisotropy

Remove the 0.5f central-difference scaling factor from gradient and
laplacian computation. The factor cancels in angle ratios (cos^2 theta,
sin^2 theta, cos theta sin theta) since they are computed as gx^2/m^2,
gy^2/m^2, gx gy/m^2. For the magnitude term, precompute
half_anisotropy[k] = anisotropy[k] * 0.5f outside the pixel loop.
This eliminates 4 float multiplies per pixel per channel from the hot path.
```

Line 1: commit message title. Remainder: commit body description.

**After completion, the script appends:**

On success:
```
outcome: improvement
commit: a1b2c3d
Reduced sum(user) from 35.5s to 34.2s (~3.7% improvement)
```

On failure (no benchmark ran):
```
outcome: build failure
```
or `outcome: quality regression` or `outcome: not applicable`.
In the `not applicable` case, the AI's explanation is appended after the outcome.

On failure (benchmark ran — QA passed but performance check failed):
```
outcome: performance regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.561 | 5.372 |

# Totals
...
```

When the QA gate passes and a benchmark runs, the performance table is always appended to the idea file in `done/`, regardless of whether the idea succeeded or failed. This provides full context for strategy reviews without needing separate perf-log files for failed ideas.

Individual perf-log files in `perf-logs/` are only created for successful ideas.

The perf summary line is always computed by the Python script, never by the LLM.

### Directory Transitions

```
ideas/todo/     → ideas/coding/    (selection)
ideas/coding/   → ideas/testing/   (build succeeded)
ideas/coding/   → ideas/done/      (build retries exhausted)
ideas/testing/  → ideas/done/      (quality/benchmark result, pass or fail)
```

### Generation

- Count ideas in `ideas/todo/`.
- If fewer than `min_ideas`: call LLM to batch-generate `(min_ideas - count)` ideas in a single call.
- The generation prompt includes all existing idea titles as a hint to avoid repeats.
- Write all generated ideas to `ideas/todo/`, prefixed with a `yyyy-mm-dd-hh-mm-ss-` timestamp so lexicographic order reflects creation time.
- Commit script repo: "generated N new ideas".

### Selection

- Pick the first idea lexicographically from `ideas/todo/` (`sorted(list_ideas(...))[0]`).
- Timestamp prefixes ensure FIFO ordering among generated ideas.
- Users can force priority by prefixing filenames with digits (e.g., `000-urgent`), which sort before any timestamp.
- Move the selected file to `ideas/coding/`.

---

## 5. Learnings

A single file: `learnings.md` in the script repo root.

- Maintained by the LLM during strategy review steps.
- The LLM gets Read + Edit tools on the script repo to update it.
- Structure (guidance, not enforced): `## What works` / `## What to avoid`.
- Committed by the script after each review.

Learnings evolve over time. The LLM may update, remove, or add entries based on accumulated evidence. Early learnings may be refined or invalidated as more experiments complete.

The script commits `learnings.md` before and after the LLM edits it, providing a full edit trail via git history.

---

## 6. Performance Testing

### Benchmark Output Format

The external benchmark script MUST output one or more lines in the format:

```
user=0.561, cpu=5.372
user=0.123
user=0.234, cpu=0.051, gpu=0.180
```

- `user` is mandatory on every line.
- Other labels (cpu, gpu, etc.) are informational.
- Lines from the same script will have consistent structure across runs (same number of lines; line N always has the same labels).

### Convergence Loop

The orchestrator handles benchmark repetition and convergence. The external script only needs to run once and print results. **No timeouts are imposed on subprocess calls** — benchmarks (and build/quality commands) may run for arbitrarily long periods.

1. **Warmup:** Run `bench_cmd` `num_warmup_iterations` times. Discard all output. No early abort checks during warmup.
2. **First real run:**
   - Parse output.
   - Store as element-wise best.
   - Early abort: if `sum(user) > baseline_sum * (1 - min_improvement_pct / 100)`, the first run doesn't meet the improvement threshold — abort benchmark, report failure. This catches both regressions and insufficient improvements, avoiding ~30 min of futile convergence runs. The `BenchmarkError` carries the partial rows so they can be recorded on the idea file.
3. **Subsequent runs:**
   - Parse output. If output cannot be parsed (missing `user`, wrong number of lines, malformed values), treat as benchmark parse error → FAIL_IDEA (outcome: "benchmark error").
   - Update element-wise best (per-row minimum for each label).
   - Compute improvement: compare current `sum(user)` of element-wise bests against the `sum(user)` of element-wise bests at the point when the tail counter was last reset (or first run, if never reset).
   - If improvement < `benchmark_convergence_threshold_pct`: increment tail counter.
   - Else: reset tail counter, record current element-wise-best `sum(user)` as new reference point.
   - If tail counter >= `benchmark_convergence_tail_runs`: stop.
4. **Result:** Element-wise best values across all runs. The final result captures all improvements including sub-threshold ones from the tail.

### Success Evaluation

```python
baseline_sum = sum(user) from current-best-perf.md
result_sum = sum(user) from benchmark result
improvement_pct = (baseline_sum - result_sum) / baseline_sum * 100

# Gate 1: minimum improvement
if improvement_pct < min_improvement_pct:
    fail

# Gate 2: individual regression tradeoff
max_row_regression_pct = max(
    (result_row - baseline_row) / baseline_row * 100
    for each row where result_row > baseline_row
)
if max_row_regression_pct > 0 and improvement_pct < individual_regression_tradeoff * max_row_regression_pct:
    fail

success
```

### Performance Log Files

The `perf-logs/` directory contains only two files:
- `perf-logs/baseline-perf.md` — initial baseline measurement (useful for the final PR).
- `perf-logs/current-best-perf.md` — updated after each successful optimisation (used to evaluate the next idea).

No per-idea perf-log files are created. Instead, the performance table is appended directly to the idea file in `ideas/done/` whenever a benchmark runs (see Idea File Format above). This includes early-abort results (single-run, no convergence), which are still informative for diagnosing what went wrong.

Format:

```markdown
# Individual timings
| user | cpu | gpu |
| ---- | --- | --- |
| 0.551 | 5.372 | |
| 0.123 | | |
| 0.234 | 0.051 | 0.180 |

# Totals
| user | cpu | gpu |
| ---- | --- | --- |
| 0.908 | 5.423 | 0.180 |

# Averages
| user | cpu | gpu |
| ---- | --- | --- |
| 0.303 | 2.712 | 0.180 |
```

- **Totals:** Missing values treated as 0.
- **Averages:** Missing values excluded from computation (only average over rows that have the label).
- **Decimal places:** Maximum precision from input values, with rounding.

---

## 7. AI Module

### Providers

Hardcoded: claude and gemini. Same CLI invocation patterns as the current orchestrator. To be made configurable in a future iteration.

### Failover

Random provider selection per call. On failure, disable the failed provider. If all providers exhausted, wait 5 minutes, re-enable all, retry. This waiting loop runs indefinitely (costs nothing) and is safe to interrupt (Ctrl+C) — no processing is in progress during the wait. Providers are reset at the start of each main loop iteration.

### Roles

All roles use the "best" tier (opus for claude, pro for gemini).

| Role | Tools | Receives |
|------|-------|----------|
| Generate ideas | Read (target repo) | instructions + learnings + existing idea titles + count needed |
| Select idea | Read (target repo) | all todo idea contents |
| Implement | Read + Edit (target repo) | instructions + learnings + idea content + errors.txt if retry |
| Review learnings | Read + Edit (script repo) | instructions + all done idea contents |

### Implementation Prompt — Build/Test Prohibition

The implementation prompt MUST contain at minimum three separate, prominently formatted prohibitions against running builds, tests, or benchmarks. These must use strong language including explicit penalty warnings. This is a hard requirement driven by observed agent non-compliance with softer instructions.

The agent may use Read tools to explore the target codebase (including using language servers like clangd to search references), but MUST NOT execute any build, test, or benchmark commands.

### Tool Scoping

LLM CLI tools are scoped by setting the working directory (`cwd`) to the appropriate repo root when invoking the LLM process. For implementation and generation/selection calls, `cwd` is set to the target repo. For review calls, `cwd` is set to the script repo.

---

## 8. State Machine

### Startup

Recovery-aware startup. The checks are ordered so that in-progress work is
detected BEFORE any unconditional cleanup.

```
STARTUP
  multiple files in ideas/coding/ or ideas/testing/?
    → error: "unexpected state: multiple files in <dir>. Please investigate.", exit

  idea in ideas/testing/?
    target repo dirty?
      → go to TEST (edits are present, build had succeeded)
    target repo clean?
      → move idea to ideas/coding/, clean errors.txt, go to CODE

  idea in ideas/coding/?
    target repo dirty?
      → rollback target, clean errors.txt, go to CODE
    target repo clean?
      → clean errors.txt, go to CODE

  target repo dirty? (no idea in coding or testing — orphan dirty state)
    → rollback target

  perf-logs/ empty? → BASELINE
  else → GENERATE
```

### Baseline Establishment

```
BASELINE
  verify target repo clean and on correct branch (hard fail if not)
  build (hard fail on error, no retries)
  quality check if configured (hard fail on error, no retries)
    Note: unlike req.md which suggests skipping quality at baseline, we run it
    if configured — better to catch issues before starting optimisation.
  benchmark (full convergence loop)
  save perf-logs/baseline-perf.md
  copy to perf-logs/current-best-perf.md
  commit script repo: "<commit_prefix> established baseline"
  → GENERATE
```

### Main Loop

```
GENERATE
  count ideas in ideas/todo/
  if < min_ideas:
    LLM batch-generates (min_ideas - count) ideas in a single call
    write new ideas to ideas/todo/
    commit script repo: "generated N new ideas"
  if LLM failed to produce parseable ideas → retry (loop back to GENERATE)
  pick first idea lexicographically from ideas/todo/
  move to ideas/coding/
  → CODE

CODE
  script builds prompt: instructions + learnings + idea content
  if errors.txt exists: append to prompt with fix instructions
  LLM gets Read + Edit tools for target repo
  if LLM responds NOT_APPLICABLE → FAIL_IDEA (outcome: "not applicable", includes explanation)
  → BUILD

BUILD
  script runs build_cmd in target repo
  success → move idea to ideas/testing/, → TEST
  failure →
    save build output to ideas/coding/errors.txt
    retries remaining? → CODE
    retries exhausted → FAIL_IDEA (outcome: "build failure")

TEST
  quality_cmd not configured → BENCHMARK
  script runs quality_cmd in target repo
  success → BENCHMARK
  failure →
    move idea back to ideas/coding/
    save test output to ideas/coding/errors.txt
    retries remaining? → CODE
    retries exhausted → FAIL_IDEA (outcome: "quality regression")

BENCHMARK
  warmup: run bench_cmd num_warmup_iterations times, discard
  convergence loop (see Section 6)
  evaluate result (see Section 6)
  success → SUCCESS_IDEA
  failure (performance) → FAIL_IDEA (outcome: "performance regression")
  failure (early abort) → FAIL_IDEA (outcome: "benchmark early abort: <error details>")
  failure (parse error) → FAIL_IDEA (outcome: "benchmark error")

SUCCESS_IDEA
  commit target repo (only files under `commit_scope` prefixes):
    title: "<commit_prefix>: <idea line 1>"
    body: idea description
    trailer: perf summary (computed by script)
  get commit hash
  move idea to ideas/done/, append outcome + commit hash + perf summary + perf table
  update perf-logs/current-best-perf.md
  commit script repo
  reset consecutive perf failure counter
  → CHECK_TERMINATION

FAIL_IDEA
  rollback target repo
  move idea to ideas/done/, append outcome
  if benchmark ran (incl. early abort): append perf table to idea file
  commit script repo
  increment consecutive perf failure counter (only for "performance regression";
    NOT for "build failure", "quality regression", "benchmark early abort: ...", or "benchmark error")
  → CHECK_TERMINATION

CHECK_TERMINATION (after CODE/TEST)
  max_iterations reached? → TERMINATE
  max_consecutive_perf_failures reached? → TERMINATE
  max_runtime_minutes exceeded? → TERMINATE
  periodic review due (iteration % review_frequency == 0)? → REVIEW
  → GENERATE

Note: idea exhaustion is NOT checked here. An empty todo/ after an idea
completes is normal — GENERATE will create more. Idea exhaustion is only
detected in GENERATE after deduplication — when the LLM generates ideas
but all are duplicates of previously tried ideas (no new, genuine ideas).
If the LLM fails to produce any parseable output (not dedup-related),
the loop retries via GENERATE without declaring exhaustion.

The iteration counter increments each time an idea enters CODE (i.e., each
idea attempt). GENERATE runs that only top up the idea pool without
attempting an idea do not increment the counter.

REVIEW
  LLM reads all ideas/done/, edits learnings.md (Read + Edit on script repo)
  commit script repo: "updated learnings"
  → GENERATE

TERMINATE
  log reason for termination
  exit
```

### Retry Counter

A single retry counter is shared across build and quality check failures within one idea. It resets when a new idea is selected. It is NOT persisted across script restarts — by design, a restart gets a fresh set of retries. This is acceptable because the target repo is rolled back on restart, so the LLM re-implements from scratch; the prior retry history is irrelevant.

When retries are exhausted, the outcome recorded on the idea reflects the type of the **last** failure (build failure or quality regression), regardless of the mix of failure types during retries.

### Script Repo Commits

The script repo is committed at these points:
1. Baseline established.
2. New ideas generated (batch).
3. Idea fully resolved (moved to done with outcome).
4. Learnings updated.
5. Performance log updated (typically same commit as idea resolution).

---

## 9. Termination Conditions

Three conditions are checked after each idea completes (in CODE and TEST paths):

1. **Max iterations:** `max_iterations` reached.
2. **Stagnation:** `max_consecutive_perf_failures` consecutive ideas with outcome "performance regression" only. Build failures, quality regressions, benchmark early aborts, and benchmark errors do NOT count — they reflect tooling/coding issues, not exhaustion of the optimisation space.
3. **Time limit:** `max_runtime_minutes` exceeded.

Manual stop (Ctrl+C) is handled by startup recovery on next run.

---

## 10. Development Approach

Test-driven development (TDD). Tests written before implementation for each module. The modular package structure supports testing each concern in isolation:

- `test_settings.py` — parsing, validation, defaults, init scaffolding.
- `test_state.py` — idea file creation, sanitisation, directory transitions.
- `test_benchmark.py` — output parsing, convergence logic, stats computation, success evaluation.
- `test_git.py` — branch resolution, commit, rollback, dirty checks (against real or mock git repos).
- `test_prompts.py` — prompt construction for each role.
- `test_runner.py` — state machine transitions, termination conditions, retry logic.
