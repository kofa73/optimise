# Gemini Project Context: Optimiser

This project is an autonomous, LLM-powered performance optimization tool. It drives a "Two-Repository" loop where it generates optimization ideas, implements them in a target repository, reviews the code, benchmarks the results, and commits successful improvements.

## Project Overview

- **Purpose**: Automate the performance optimization of a target codebase (e.g., Image Processing (IOP) in Darktable) using LLMs.
- **Architecture**:
    - **Script Repository**: The current directory, containing the `optimiser` script, configuration, state (`ideas/`), and performance logs (`perf-logs/`).
    - **Target Repository**: The repository being optimized (e.g., `/workspace/darktable`).
- **Technologies**: Python 3.10+, Git, Pytest, and LLM APIs (Claude/Gemini).
- **Core Loop (State Machine)**:
    `BASELINE → GENERATE → CODE → CODE_REVIEW → BUILD → QUALITY → BENCHMARK → SUCCESS/FAIL`

## Key Commands

### Main Loop
- **Initialize workspace**: `python3 optimise.py init` (Scaffolds a new script repo).
- **Run optimization**: `python3 optimise.py run` (Starts the autonomous optimization loop).

### Standalone Testing & Benchmarking
- **Full build & test**: `python3 optimise.py test`
- **Manual benchmark**: `python3 optimise.py benchmark`
- **Quality check**: `python3 optimise.py qualitycheck`
- **Historical testing**: Any command can take a `[commit_id]` to test a specific version (e.g., `python3 optimise.py benchmark a1b2c3d`).

### Internal Tests
- **Run all tests**: `python3 -m pytest tests/ -v`

## Project Structure & State

- **`optimise/`**: Core logic (CLI, Git wrapper, Benchmark loop, Prompt builders).
- **`ideas/`**:
    - `todo/`: New ideas waiting for implementation.
    - `coding/`: The currently active idea being implemented.
    - `testing/`: Ideas being built/benchmarked.
    - `done/`: Completed experiments (Success/Fail/Not Applicable).
- **`perf-logs/`**:
    - `baseline-perf.md`: Original performance before optimizations.
    - `current-best-perf.md`: Best performance achieved so far.
- **`settings.conf`**: Main configuration for paths, commands, and thresholds.
- **`instructions.md`**: Domain-specific instructions for the LLM.
- **`learnings.md`**: LLM-maintained summary of what works and what to avoid.

## Development Conventions

- **TDD (Test-Driven Development)**: Write failing tests in `tests/` before implementing features or fixing bugs in `optimise/`.
- **Surgical Code Review**: The system includes an automated code review step that checks for:
    - Stale comments.
    - Giant macro misuse.
    - Unswitched loop duplication.
    - Specialization-boundary regressions such as moving `DT_OMP_FOR()` into a generic helper that takes hot-path flags as parameters.
    - OpenCL contamination in CPU paths.
- **Performance Integrity**:
    - Benchmarks use a convergence loop (`benchmark_convergence_tail_runs`) to stabilize results.
    - Element-wise best tracking ensures measurements aren't skewed by noise.
    - Only improvements meeting `min_improvement_pct` without regressing more than `max_regression_pct` are committed.
