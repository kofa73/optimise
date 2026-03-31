# Optimiser

A Python tool that uses LLMs to automate codebase performance optimization. It runs an autonomous loop that generates ideas, modifies code, verifies build and quality metrics, and benchmarks performance before committing changes.

## Methodology

Optimiser uses a **Two-Repository Architecture**:
- **Script Repository**: Stores configurations, idea states, and LLM context.
- **Target Repository**: The codebase being modified. This ensures only successful, benchmarked commits are added to the git history.

The system runs a **Continuous Optimization Loop** with the following lifecycle:

1. **Creation (`ideas/todo`)**: When the idea queue is empty, the LLM reads `instructions.md` and `learnings.md` to generate a batch of new optimization ideas, ordered by expected improvement (most impactful first). Each idea filename is prefixed with an ordinal number and timestamp for deterministic execution order.
2. **Coding (`ideas/coding`)**: The next idea is selected. The LLM modifies the specified files in the `target_repo`.
3. **Code Review**: A cheaper LLM (normal tier) reviews the diff against a narrow checklist: stale comments, giant macro misuse, unswitched code duplication, specialization-boundary regressions (for example moving `DT_OMP_FOR()` into a generic helper that takes hot-path flags as parameters), and OpenCL contamination. If rejected, feedback is sent back to the coding LLM for a retry.
4. **Testing (`ideas/testing`)**: The system runs the user-configured build and quality checks. If either fails, the error logs are provided to the LLM to attempt a fix.
5. **Benchmarking**: If the build and quality checks pass, the changes are benchmarked. A convergence loop is used to measure the performance difference against the current baseline.
6. **Done (`ideas/done`)**:
   - **Success**: The changes are committed to the target repository along with their benchmark results, the baseline is updated, and the idea is marked complete.
   - **Failure**: If performance degrades or build retries are exhausted, the modified files are rolled back using git. The idea is logged with its failure outcome.

When the idea queue is empty and completed ideas exist, a **Strategy Review** runs before generating new ideas. The LLM evaluates completed ideas and updates `learnings.md` with successful patterns and approaches to avoid.

## Prerequisites

Before using Optimiser, ensure the following:
1. **AI CLI Tools**: You must have at least one of `claude` (Claude Code) or `gemini` (Gemini CLI) installed and authenticated on your system.
2. **Project Environment**: Your target project must be fully buildable and testable from the command line. Ensure all dependencies, virtual environments, and system libraries required by your build, benchmark, and quality check commands are installed and configured.

## User Instructions

### 1. Initialize the Workspace
Create a directory to act as your Script Repository:
```bash
mkdir opt-workspace
cd opt-workspace
python /path/to/optimiser/optimise.py init
```

### 2. Configure Settings
Edit `settings.conf` to configure the required paths and commands:
- `target_repo`: Absolute path to the codebase to optimize.
- `branch`: The git branch the tool will modify.
- `optimisation_target`: The source file(s) the LLM is allowed to modify.
- `build_cmd`, `bench_cmd`, `quality_cmd`: Shell commands to build, benchmark, and run test suites.
- `commit_scope`: The directory scope for dirty file checks and rollbacks (e.g., `src/`).
- `targeting_mode`: (Optional) `overall` (default) optimises sum(user) across all benchmark instances. `least_improved_instance` dynamically targets the instance that has improved least since baseline.
- `max_regression_pct`: (Optional) Maximum allowed regression on the guard measure (percent). In `overall` mode, no individual instance may regress more than this. In `least_improved_instance` mode, sum(user) must not regress more than this. Defaults to `3`.
- `disabled_providers`: (Optional) A comma-separated list of AI providers to permanently disable (e.g., `claude` or `gemini`). Providers missing required system binaries are also permanently disabled automatically.
- `llm_timeout`: (Optional) Maximum time in seconds to wait for an LLM response before timing out. Defaults to `3600`.

Next, document the specific optimization goals for the LLM in `instructions.md`.

### 3. Run the Loop
Start the main optimization loop:
```bash
python /path/to/optimiser/optimise.py run
```
The script can be stopped with `Ctrl+C`. On restart, a startup recovery sequence handles any orphaned state files or uncommitted changes in the target repository.

### 4. Standalone Commands
Individual stages of the optimization pipeline can be executed manually. Note that all of these commands automatically execute the `build_cmd` first to ensure the codebase is compiled before testing or benchmarking:
```bash
python /path/to/optimiser/optimise.py build
python /path/to/optimiser/optimise.py qualitycheck
python /path/to/optimiser/optimise.py benchmark
python /path/to/optimiser/optimise.py test      # Runs qualitycheck followed by benchmark
```
**Historical Testing**: You can append an optional git `[commit_id]` to the end of any standalone command (e.g., `python /path/to/optimiser/optimise.py benchmark a1b2c3d`). This extracts and tests the configured `optimisation_target` files from that specific commit in the target directory.
