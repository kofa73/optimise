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
        capture_output=True, text=True, cwd=cwd,
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


class TerminationReason(enum.Enum):
    MAX_ITERATIONS = "max iterations reached"
    STAGNATION = "no performance improvement"
    TIME_LIMIT = "time limit exceeded"


def check_termination(iteration, max_iterations, consecutive_perf_failures,
                      max_consecutive, start_time, max_minutes):
    """Check if any termination condition is met.

    Returns a TerminationReason or None.
    """
    if iteration >= max_iterations:
        return TerminationReason.MAX_ITERATIONS
    if consecutive_perf_failures >= max_consecutive:
        return TerminationReason.STAGNATION
    elapsed_minutes = (time.time() - start_time) / 60
    if elapsed_minutes >= max_minutes:
        return TerminationReason.TIME_LIMIT
    return None


from optimise.benchmark import (
    parse_bench_output, update_element_best, sum_user,
    ConvergenceState, BenchmarkError,
)


def run_benchmark_loop(bench_cmd, cwd, baseline_user_sum,
                       num_warmup, convergence_threshold_pct,
                       convergence_tail_runs, early_abort_pct):
    """Run the benchmark convergence loop.

    Returns element-wise best rows on success.
    Raises BenchmarkError on early abort or parse failure.
    """
    # Warmup
    for i in range(num_warmup):
        log.info(f"BENCH warmup {i+1}/{num_warmup}")
        subprocess.run(
            bench_cmd, shell=True,
            capture_output=True, text=True, cwd=cwd,
        )

    best = None
    convergence = ConvergenceState(convergence_threshold_pct, convergence_tail_runs)
    run_idx = 0

    while True:
        run_idx += 1
        log.info(f"BENCH run {run_idx}")

        result = subprocess.run(
            bench_cmd, shell=True,
            capture_output=True, text=True, cwd=cwd,
        )
        rows = parse_bench_output(result.stdout)
        best = update_element_best(best, rows)
        current_sum = sum_user(best)

        # Early abort on first real run: must already beat improvement threshold
        if run_idx == 1:
            threshold = baseline_user_sum * (1 - early_abort_pct / 100)
            if current_sum > threshold:
                improvement_pct = (1 - current_sum / baseline_user_sum) * 100
                raise BenchmarkError(
                    f"Benchmark early abort: {current_sum:.3f}s vs "
                    f"baseline {baseline_user_sum:.3f}s "
                    f"({improvement_pct:+.1f}%, need {early_abort_pct}%)",
                    rows=best,
                )

        convergence.update(current_sum)
        log.info(f"BENCH run {run_idx}: sum(user)={current_sum:.3f}s "
                 f"(tail={convergence.tail_counter}/{convergence_tail_runs})")

        if convergence.converged:
            log.info(f"BENCH converged after {run_idx} runs")
            break

    return best


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


def parse_not_applicable(text):
    """Check if the LLM response indicates the idea is not applicable.

    Returns (is_not_applicable: bool, explanation: str).
    The explanation is the rest of the text after NOT_APPLICABLE.
    """
    lines = text.strip().split("\n")
    if not lines:
        return False, ""

    first_line = lines[0].strip()
    if first_line == "NOT_APPLICABLE":
        explanation = "\n".join(lines[1:]).strip()
        return True, explanation

    return False, ""


