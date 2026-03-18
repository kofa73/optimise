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


import sys
import time

from optimise.settings import parse_settings, validate_settings, SettingsError
from optimise.git import GitRepo, GitError
from optimise.ai import AIRouter
from optimise.runner import (
    determine_startup_state, StartupState, TerminationReason,
    check_termination, run_shell_step, run_benchmark_loop,
    parse_generated_ideas, parse_not_applicable,
)
from optimise.state import (
    list_ideas, move_idea, read_idea, create_idea, append_outcome,
    all_idea_titles, clean_errors, sanitise_filename,
)
from optimise.benchmark import (
    format_perf_log, parse_perf_log, evaluate_success, sum_user, BenchmarkError,
)
from optimise.prompts import (
    build_generation_prompt,
    build_implementation_prompt, build_review_prompt,
)


import enum


def _read_learnings(directory):
    """Read learnings.md content."""
    path = os.path.join(directory, "learnings.md")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


class GenerationResult(enum.Enum):
    OK = "ok"
    LLM_FAILURE = "llm_failure"


def _generate_ideas(directory, settings, ai, target_repo_path, instructions, target_files):
    """Generate ideas in a single batch.

    Returns GenerationResult:
      OK           — ideas were added, or todo already had enough
      LLM_FAILURE  — LLM failed to produce any parseable ideas
    """
    todo_count = len(list_ideas(directory, "todo"))
    needed = settings["min_ideas"] - todo_count

    if needed <= 0:
        return GenerationResult.OK

    learnings = _read_learnings(directory)
    existing_titles = all_idea_titles(directory)

    prompt = build_generation_prompt(
        instructions, learnings, existing_titles, needed, target_files,
    )
    output, rc, provider = ai.call(
        prompt, tier="best", cwd=target_repo_path,
    )
    if rc != 0:
        log.warning(f"Idea generation failed ({provider})")
        return GenerationResult.LLM_FAILURE

    ideas = parse_generated_ideas(output)
    if not ideas:
        return GenerationResult.LLM_FAILURE

    for idea in ideas:
        content = f"{idea['title']}\n\n{idea['description']}"
        create_idea(directory, idea["filename"], content)

    return GenerationResult.OK


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
            log.info("[BASELINE] Establishing baseline...")

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
                    early_abort_pct=settings["early_abort_pct"],
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
            log.info(f"[BASELINE] Established: sum(user)={sum_user(best):.3f}s")
            state = StartupState.GENERATE
            continue

        if state == StartupState.GENERATE:
            todo_before = len(list_ideas(directory, "todo"))
            gen_result = _generate_ideas(
                directory, settings, ai, target_repo_path,
                instructions, target_files,
            )
            todo_after = len(list_ideas(directory, "todo"))
            if todo_after > todo_before:
                script_git.commit_all(
                    f"generated {todo_after - todo_before} new ideas"
                )

            if gen_result == GenerationResult.LLM_FAILURE:
                log.warning("[GENERATE] All LLM providers failed — "
                            "will retry after cooldown")
                continue

            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

            # Pick first idea lexicographically
            todo_files = sorted(list_ideas(directory, "todo"))
            selected = todo_files[0]
            move_idea(directory, selected, "todo", "coding")
            log.info(f"[GENERATE] Selected idea: {selected}")
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
            log.info(f"[CODE] Implementing idea: {idea_title[:80]}")
            output, rc, provider = ai.call(
                prompt, tier="best", cwd=target_repo_path, allow_edits=True,
            )

            if rc != 0:
                log.error(f"[CODE] AI implementation failed ({provider})")
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

            # Check if LLM says idea is not applicable
            is_na, explanation = parse_not_applicable(output)
            if is_na:
                log.info(f"[CODE] Idea not applicable: {idea_title[:60]}")
                state_obj = _BuildState(directory, target_repo_path, target_git,
                                       script_git, settings, idea_file, iteration,
                                       consecutive_perf_failures, start_time)
                _fail_idea(state_obj, "not applicable", explanation=explanation)
                state = StartupState.GENERATE
                continue

            state_obj = _BuildState(directory, target_repo_path, target_git,
                               script_git, settings, idea_file, iteration,
                               consecutive_perf_failures, start_time)
            # Fall through to BUILD
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
    """Bundle of state for the build->test->benchmark pipeline."""
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
    """Run the BUILD->TEST->BENCHMARK pipeline.

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
            early_abort_pct=s.settings["early_abort_pct"],
        )
    except BenchmarkError as e:
        log.error(f"Benchmark error: {e}")
        if e.rows:
            return _fail_idea(s, f"benchmark early abort: {e}",
                              bench_rows=e.rows)
        return _fail_idea(s, "benchmark error")

    # Evaluate
    ok, improvement_pct, detail = evaluate_success(
        baseline_rows, best,
        s.settings["min_improvement_pct"],
        s.settings["individual_regression_tradeoff"],
    )

    if ok:
        return _succeed_idea(s, best, improvement_pct, detail, baseline_sum)
    else:
        log.info(f"FAILED: {detail}")
        return _fail_idea(s, "target not reached", bench_rows=best)


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

    # Commit target repo (only files under commit_scope)
    scope = s.settings.get("commit_scope", ["src/"])
    s.target_git.commit_changed(f"{commit_title}\n\n{commit_body}", scope=scope)
    commit_hash = s.target_git.get_commit_hash()
    log.info(f"SUCCESS: {perf_line} (commit {commit_hash})")

    # Move idea to done
    perf_table = format_perf_log(best)
    move_idea(s.script_repo, s.idea_file, "testing", "done")
    append_outcome(s.script_repo, s.idea_file, "improvement",
                   commit_hash=commit_hash, perf_summary=perf_line,
                   perf_table=perf_table)

    # Update current best
    current_best_path = os.path.join(s.script_repo, "perf-logs", "current-best-perf.md")
    with open(current_best_path, "w") as f:
        f.write(perf_table)

    s.script_git.commit_all(f"idea succeeded: {idea_title[:60]}")

    return {"consecutive_perf_failures": 0}


def _fail_idea(s, outcome, bench_rows=None, explanation=None):
    """Handle a failed idea."""
    # Determine which directory the idea is currently in
    for subdir in ("testing", "coding"):
        if list_ideas(s.script_repo, subdir) and \
           s.idea_file in list_ideas(s.script_repo, subdir):
            move_idea(s.script_repo, s.idea_file, subdir, "done")
            break

    perf_table = format_perf_log(bench_rows) if bench_rows else None
    append_outcome(s.script_repo, s.idea_file, outcome, perf_table=perf_table,
                   explanation=explanation)
    s.target_git.rollback()
    clean_errors(s.script_repo)

    idea_title, _ = read_idea(s.script_repo, "done", s.idea_file)
    s.script_git.commit_all(f"idea failed ({outcome}): {idea_title[:60]}")

    cpf = s.consecutive_perf_failures
    if outcome == "target not reached":
        cpf += 1

    return {"consecutive_perf_failures": cpf}


def _do_review(directory, script_git, ai, instructions, target_repo_path):
    """Run the periodic strategy review."""
    log.info("[REVIEW] Running strategy review...")
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
