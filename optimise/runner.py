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
