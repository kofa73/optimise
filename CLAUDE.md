# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run a single test file
python3 -m pytest tests/test_benchmark.py -v

# Run a single test class or method
python3 -m pytest tests/test_cli.py::TestDoBuildTestBenchmark -v
python3 -m pytest tests/test_state.py -k test_creates_file_in_todo -v
```

No build step, linter, or formatter is configured. The project is pure Python 3.10+.

## Architecture

**Two-repository model:** The optimiser (script repo) drives autonomous LLM-powered performance optimisation of a separate target repo. Only successful, benchmarked changes get committed to the target.

### State Machine (`optimise/cli.py`)

The core loop in `do_run()` cycles through states:

```
BASELINE → GENERATE → CODE → CODE_REVIEW → BUILD/TEST/BENCHMARK → SUCCESS/FAIL → GENERATE → ...
```

- **BASELINE**: Run benchmark to establish `perf-logs/baseline-perf.md` and `perf-logs/current-best-perf.md`
- **GENERATE**: Produce idea batch via LLM (`ideas/todo/`), optionally run strategy review
- **CODE**: LLM implements the idea, editing files in the target repo
- **CODE_REVIEW**: Cheaper LLM (normal tier) reviews the diff against a narrow checklist (stale comments, macro misuse, unswitched duplication, OpenCL contamination). Rejected → feedback loops back to CODE. Approved → proceeds to BUILD
- **BUILD→TEST→BENCHMARK**: Pipeline in `_do_build_test_benchmark()`. On failure, retries with error context. On success, commits to target repo and updates current-best perf log

Startup recovery (`determine_startup_state()` in `runner.py`) detects orphan states and resumes correctly after crashes.

### Module Responsibilities

| Module | Role |
|---|---|
| `cli.py` | Entry point (`do_run`, `do_init`, `do_command`), state machine, idea flow |
| `runner.py` | Startup state detection, shell step execution, benchmark convergence loop, termination checks |
| `benchmark.py` | Parse benchmark output (`label=value` format), element-wise best tracking, convergence detection, success evaluation |
| `settings.py` | Parse `settings.conf` (key: value), validate types/paths, templates for `init` |
| `ai.py` | `AIRouter` — route calls to Claude CLI or Gemini CLI with failover |
| `prompts.py` | Build LLM prompts for idea generation, implementation, code review, and strategy review |
| `state.py` | Idea lifecycle: create/list/move/read ideas across `todo/coding/testing/done` |
| `git.py` | `GitRepo` wrapper — dirty checks, scoped rollback, commit, branch management |

### Key Concepts

- **`commit_scope`**: Path prefixes (e.g. `src/iop/`) restricting which files the optimiser may commit or rollback in the target repo
- **`evaluate_success()`**: Two-check model — target measure must improve by `min_improvement_pct`, guard measure must not regress beyond `max_regression_pct`
- **Convergence**: Benchmark runs repeat until element-wise best stabilises (tail counter hits `convergence_tail_runs`)
- **Early abort**: First benchmark run checked against `early_abort_pct` threshold vs current-best to avoid wasting time on clearly-worse changes
- **Idea files**: Markdown in `ideas/<stage>/`, filename = `NNN-YYYY-MM-DD-HH-MM-SS-slug.md`, first line = title, rest = body

### Data Flow

```
settings.conf → validate_settings() → settings dict
                                          ↓
perf-logs/current-best-perf.md ← format_perf_log(best_rows)
                                          ↑
target repo ← LLM edits ← build_implementation_prompt()
                                          ↑
ideas/todo/*.md ← parse_generated_ideas() ← build_generation_prompt()
```
