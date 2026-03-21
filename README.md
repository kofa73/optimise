# Optimiser

A Python tool that uses LLMs to automate codebase performance optimization. It runs an autonomous loop that generates ideas, modifies code, verifies build and quality metrics, and benchmarks performance before committing changes.

## Methodology

Optimiser uses a **Two-Repository Architecture**:
- **Script Repository**: Stores configurations, idea states, and LLM context.
- **Target Repository**: The codebase being modified. This ensures only successful, benchmarked commits are added to the git history.

The system runs a **Continuous Optimization Loop** with the following lifecycle:

1. **Creation (`ideas/todo`)**: The LLM reads `instructions.md` and `learnings.md` to generate new optimization ideas when the queue is low.
2. **Coding (`ideas/coding`)**: The next idea is selected. The LLM modifies the specified files in the `target_repo`.
3. **Testing (`ideas/testing`)**: The system runs the user-configured build and quality checks. If either fails, the error logs are provided to the LLM to attempt a fix.
4. **Benchmarking**: If the build and quality checks pass, the changes are benchmarked. A convergence loop is used to measure the performance difference against the current baseline.
5. **Done (`ideas/done`)**:
   - **Success**: The changes are committed to the target repository along with their benchmark results, the baseline is updated, and the idea is marked complete.
   - **Failure**: If performance degrades or build retries are exhausted, the modified files are rolled back using git. The idea is logged with its failure outcome.

Periodically, a **Strategy Review** runs. The LLM evaluates completed ideas and updates `learnings.md` with successful patterns and approaches to avoid.

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
- `disabled_providers`: (Optional) A comma-separated list of AI providers to permanently disable (e.g., `claude` or `gemini`). Providers missing required system binaries are also permanently disabled automatically.

Next, document the specific optimization goals for the LLM in `instructions.md`.

### 3. Run the Loop
Start the main optimization loop:
```bash
python /path/to/optimiser/optimise.py run
```
The script can be stopped with `Ctrl+C`. On restart, a startup recovery sequence handles any orphaned state files or uncommitted changes in the target repository.

### 4. Standalone Commands
Individual stages of the optimization pipeline can be executed manually:
```bash
python /path/to/optimiser/optimise.py build
python /path/to/optimiser/optimise.py qualitycheck
python /path/to/optimiser/optimise.py benchmark
python /path/to/optimiser/optimise.py test      # Runs qualitycheck followed by benchmark
```
**Historical Testing**: You can append an optional git `[commit_id]` to the end of any standalone command (e.g., `python /path/to/optimiser/optimise.py benchmark a1b2c3d`). This extracts and tests the configured `optimisation_target` files from that specific commit in the target directory.
