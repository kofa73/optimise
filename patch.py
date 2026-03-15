import re
import sys

file_path = "/workspace/optimiser/docs/superpowers/plans/2026-03-14-optimiser.md"
with open(file_path, "r") as f:
    content = f.read()

def replace_or_fail(old, new, content, count=1):
    if content.count(old) != count:
        print(f"Failed to find exact match for (expected {count}, found {content.count(old)}):\n{old[:100]}...")
        sys.exit(1)
    return content.replace(old, new)

# =======================
# CHUNK 1
# =======================
old_fix1 = 'result["optimisation_target"] = targets if len(targets) > 1 else targets[0]'
new_fix1 = 'result["optimisation_target"] = targets'
content = replace_or_fail(old_fix1, new_fix1, content)

old_test1 = """        assert result["optimisation_target"] == ["src/main.c", "src/other.c"]

    def test_nonexistent_instructions_fails(self, tmp_path):"""
new_test1 = """        assert result["optimisation_target"] == ["src/main.c", "src/other.c"]

    def test_single_target_returns_list(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["optimisation_target"] = "src/main.c"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["optimisation_target"] == ["src/main.c"]

    def test_nonexistent_instructions_fails(self, tmp_path):"""
content = replace_or_fail(old_test1, new_test1, content)

old_state_imports = "from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \\\n    read_idea, append_outcome, all_idea_titles"
new_state_imports = "from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \\\n    read_idea, append_outcome, all_idea_titles, dedup_title, clean_errors"
content = replace_or_fail(old_state_imports, new_state_imports, content)

old_test_dedup = """        titles = all_idea_titles(str(tmp_path))
        assert set(titles) == {"Title A", "Title B"}
```"""
new_test_dedup = """        titles = all_idea_titles(str(tmp_path))
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
```"""
content = replace_or_fail(old_test_dedup, new_test_dedup, content)

old_commit_test = """        repo.resolve_branch("optimise-test")
        assert repo.current_branch() == "optimise-test"
```"""
new_commit_test = """        repo.resolve_branch("optimise-test")
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
```"""
content = replace_or_fail(old_commit_test, new_commit_test, content)

old_clean_errors_func = """def clean_errors(script_repo):
    \"\"\"Remove ideas/coding/errors.txt if it exists.\"\"\"
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    if os.path.exists(path):
        os.remove(path)
```"""
new_clean_errors_func = """def clean_errors(script_repo):
    \"\"\"Remove ideas/coding/errors.txt if it exists.\"\"\"
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    if os.path.exists(path):
        os.remove(path)


def save_errors(script_repo, error_output):
    \"\"\"Save build/quality error output to ideas/coding/errors.txt.\"\"\"
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    with open(path, "w") as f:
        f.write(error_output)
```"""
content = replace_or_fail(old_clean_errors_func, new_clean_errors_func, content)

old_test_save = """        coding.mkdir(parents=True)
        clean_errors(str(tmp_path))  # should not raise
```"""
new_test_save = """        coding.mkdir(parents=True)
        clean_errors(str(tmp_path))  # should not raise


class TestSaveErrors:
    def test_writes_error_file(self, tmp_path):
        from optimise.state import save_errors
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        save_errors(str(tmp_path), "error: undefined reference")
        assert (coding / "errors.txt").read_text() == "error: undefined reference"
```"""
content = replace_or_fail(old_test_save, new_test_save, content)

content = replace_or_fail('elif key != "quality_cmd" and not result[key]:', 'elif not result[key]:', content)

# =======================
# CHUNK 2
# =======================
content = replace_or_fail('def test_individual_regression_within_tradeoff_passes(self):', 'def test_individual_regression_exceeds_tradeoff_fails(self):', content)

content = replace_or_fail(r'r"(\w+)\s*=\s*(\d*\.?\d+)"', r'r"(\w+)\s*=\s*([^\s,]+)"', content)

# =======================
# CHUNK 3
# =======================

# FIX 8, 9, 11, 12

old_vars = """    start_time = time.time()
    iteration = 0
    consecutive_perf_failures = 0

    # State machine"""
new_vars = """    start_time = time.time()
    iteration = 0
    consecutive_perf_failures = 0
    retries_left = settings["max_retries"]

    # State machine"""
content = replace_or_fail(old_vars, new_vars, content)

old_generate_term = """        # Check termination (except on first pass if resuming)
        if state == StartupState.GENERATE:
            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

        ai.reset_providers()"""
new_generate_term = """        ai.reset_providers()"""
content = replace_or_fail(old_generate_term, new_generate_term, content)

old_new_idea = """            move_idea(directory, selected, "todo", "coding")
            log.info(f"Selected idea: {selected}")
            state = StartupState.CODE
            continue"""
new_new_idea = """            move_idea(directory, selected, "todo", "coding")
            log.info(f"Selected idea: {selected}")
            retries_left = settings["max_retries"]
            state = StartupState.CODE
            continue"""
content = replace_or_fail(old_new_idea, new_new_idea, content)

old_ai_fail = """            if rc != 0:
                log.error(f"AI implementation failed ({provider})")

            state = _BuildState(directory, target_repo_path, target_git,"""
new_ai_fail = """            if rc != 0:
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

            state = _BuildState(directory, target_repo_path, target_git,"""
content = replace_or_fail(old_ai_fail, new_ai_fail, content)

old_call_code = """            # Fall through to BUILD
            state_result = _do_build_test_benchmark(state)
            consecutive_perf_failures = state_result["consecutive_perf_failures"]

            if state_result.get("retry_code"):
                state = StartupState.CODE
                continue

            # Check review"""
new_call_code = """            # Fall through to BUILD
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

            # Check review"""
content = replace_or_fail(old_call_code, new_call_code, content)

old_call_test = """            state_result = _do_build_test_benchmark(state_obj)
            consecutive_perf_failures = state_result["consecutive_perf_failures"]

            if state_result.get("retry_code"):
                state = StartupState.CODE
                continue

            if iteration % settings["review_frequency"] == 0:"""
new_call_test = """            state_result = _do_build_test_benchmark(state_obj, retries_left)
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

            if iteration % settings["review_frequency"] == 0:"""
content = replace_or_fail(old_call_test, new_call_test, content)

old_do_b = """def _do_build_test_benchmark(s):
    \"\"\"Run the BUILD→TEST→BENCHMARK pipeline.

    Returns dict with "consecutive_perf_failures" and optional "retry_code".
    \"\"\"
    retries_left = s.settings["max_retries"]
    idea_subdir = "testing" if s.skip_build else "coding\"\"\""""
# I need to match the actual text
old_do_b2 = """def _do_build_test_benchmark(s):
    \"\"\"Run the BUILD→TEST→BENCHMARK pipeline.

    Returns dict with "consecutive_perf_failures" and optional "retry_code".
    \"\"\"
    retries_left = s.settings["max_retries"]
    idea_subdir = "testing" if s.skip_build else "coding\"\"\""""

content = replace_or_fail(
    'def _do_build_test_benchmark(s):\n    """Run the BUILD→TEST→BENCHMARK pipeline.\n\n    Returns dict with "consecutive_perf_failures" and optional "retry_code".\n    """\n    retries_left = s.settings["max_retries"]',
    'def _do_build_test_benchmark(s, retries_left):\n    """Run the BUILD→TEST→BENCHMARK pipeline.\n\n    Returns dict with "consecutive_perf_failures" and optional "retry_code".\n    """',
    content
)

content = replace_or_fail(
    'return {"consecutive_perf_failures": s.consecutive_perf_failures,\n                        "retry_code": True}',
    'return {"consecutive_perf_failures": s.consecutive_perf_failures,\n                        "retry_code": True, "retries_left": retries_left}',
    content, count=2
)

old_check_term = """def check_termination(iteration, max_iterations, consecutive_perf_failures,
                      max_consecutive, start_time, max_minutes):
    \"\"\"Check if any termination condition is met.

    Returns a TerminationReason or None.
    \"\"\"
    if iteration >= max_iterations:"""
new_check_term = """def check_termination(iteration, max_iterations, consecutive_perf_failures,
                      max_consecutive, start_time, max_minutes, todo_count):
    \"\"\"Check if any termination condition is met.

    Returns a TerminationReason or None.
    \"\"\"
    if todo_count == 0:
        return TerminationReason.IDEA_EXHAUSTION
    if iteration >= max_iterations:"""
content = replace_or_fail(old_check_term, new_check_term, content)

old_check_term_test = """    def test_max_iterations(self):
        reason = check_termination(
            iteration=50, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300,
        )"""
new_check_term_test = """    def test_max_iterations(self):
        reason = check_termination(
            iteration=50, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )"""
content = replace_or_fail(old_check_term_test, new_check_term_test, content)

old_check_term_test_2 = """    def test_stagnation(self):
        reason = check_termination(
            iteration=10, max_iterations=50,
            consecutive_perf_failures=5, max_consecutive=5,
            start_time=0, max_minutes=300,
        )"""
new_check_term_test_2 = """    def test_stagnation(self):
        reason = check_termination(
            iteration=10, max_iterations=50,
            consecutive_perf_failures=5, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )"""
content = replace_or_fail(old_check_term_test_2, new_check_term_test_2, content)

old_check_term_test_3 = """    def test_time_limit(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time() - 400 * 60, max_minutes=300,
        )"""
new_check_term_test_3 = """    def test_time_limit(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time() - 400 * 60, max_minutes=300, todo_count=5,
        )"""
content = replace_or_fail(old_check_term_test_3, new_check_term_test_3, content)

old_check_term_test_4 = """    def test_no_termination(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time(), max_minutes=300,
        )
        assert reason is None"""
new_check_term_test_4 = """    def test_no_termination(self):
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
        assert reason == TerminationReason.IDEA_EXHAUSTION"""
content = replace_or_fail(old_check_term_test_4, new_check_term_test_4, content)

old_exhaustion = """            if not list_ideas(directory, "todo"):
                log.info("TERMINATING: idea exhaustion")
                break"""
new_exhaustion = """            if not list_ideas(directory, "todo"):
                pass  # Handled by check_termination after the loop"""
# Wait, let's just remove the exhaustion check.
# But it says: "Remove the inline exhaustion check in the GENERATE block (replace with the check_termination result)"
# But the GENERATE block might break early before it gets to check_termination at the end of CODE or TEST.
# Let's remove it completely. Wait, if we remove it, what if todo count is 0? The loop continues to select, which might fail.
# So we still need `if not list_ideas(directory, "todo"): ... break` ? No, wait. "Remove the inline exhaustion check in the GENERATE block (replace with the check_termination result)"
# The check_termination call is now at the END of CODE/TEST block, BUT we still have to do it for GENERATE?
# Actually, the user asked to move check_termination BEFORE review in the main loop. Wait, the `GENERATE` block is earlier in the loop.
# Let's read the old file:
# ```python
#         if state == StartupState.GENERATE:
#             # Top up ideas
#             ...
#             if not list_ideas(directory, "todo"):
#                 log.info("TERMINATING: idea exhaustion")
#                 break
# ```
# If I just replace that with the `check_termination` call.
# Actually, if I move `check_termination` to after `CODE`/`TEST` block, and there's no check at the beginning, what if the first start is `GENERATE` and we exhaust ideas?
# If I replace the inline exhaustion check with `check_termination`:
old_exhaust_full = """            if not list_ideas(directory, "todo"):
                log.info("TERMINATING: idea exhaustion")
                break"""
new_exhaust_full = """            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
                len(list_ideas(directory, "todo"))
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break"""
content = replace_or_fail(old_exhaust_full, new_exhaust_full, content)


# FIX 10: Test fixture collision
old_setup_test = """    def _setup(self, script_repo, target_repo):
        \"\"\"Wire up directories and return paths.\"\"\"
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            (script_repo / d).mkdir(parents=True, exist_ok=True)
        return str(script_repo), str(target_repo)"""

# I need to find the `_setup` function in `tests/test_runner.py`
old_setup_test_full = """    def _setup(self, tmp_path):
        script_dir = tmp_path / "script"
        target_dir = tmp_path / "target"
        # ... create both as separate directories with their own git init"""
# Wait, what's currently in the file?
old_setup_actual = """    def _setup(self, script_repo, target_repo):
        \"\"\"Wire up directories and return paths.\"\"\"
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            (script_repo / d).mkdir(parents=True, exist_ok=True)
        return str(script_repo), str(target_repo)

    def test_empty_perf_logs_returns_baseline(self, tmp_path, git_repo):
        sr, tr = self._setup(tmp_path, git_repo)"""

# Instead of blindly replacing, I will handle FIX 10 carefully.
new_setup_actual = """    def _setup(self, tmp_path):
        \"\"\"Wire up directories and return paths.\"\"\"
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
        return str(script_repo), str(target_repo)"""

content = replace_or_fail(
    '    def _setup(self, script_repo, target_repo):\n        """Wire up directories and return paths."""\n        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:\n            (script_repo / d).mkdir(parents=True, exist_ok=True)\n        return str(script_repo), str(target_repo)',
    new_setup_actual, content
)

# And now replace all `self._setup(tmp_path, git_repo)` with `self._setup(tmp_path)` and adjust the `git_repo` references
# Wait, `git_repo` is used directly in the tests! E.g.: `(git_repo / ".gitkeep").write_text("dirty")`
# This means we must also replace `tmp_path, git_repo` parameter in the test with `tmp_path` and construct `git_repo = tmp_path / "target"` inside the test.
# Let's do that with regex or string replacement.

tests_to_fix = [
    ("test_empty_perf_logs_returns_baseline(self, tmp_path, git_repo):", 
     "test_empty_perf_logs_returns_baseline(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_existing_perf_logs_returns_generate(self, tmp_path, git_repo):",
     "test_existing_perf_logs_returns_generate(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_idea_in_coding_clean_target_returns_code(self, tmp_path, git_repo):",
     "test_idea_in_coding_clean_target_returns_code(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_idea_in_coding_dirty_target_rolls_back(self, tmp_path, git_repo):",
     "test_idea_in_coding_dirty_target_rolls_back(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_idea_in_testing_dirty_target_returns_test(self, tmp_path, git_repo):",
     "test_idea_in_testing_dirty_target_returns_test(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_idea_in_testing_clean_target_moves_to_coding(self, tmp_path, git_repo):",
     "test_idea_in_testing_clean_target_moves_to_coding(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_multiple_ideas_in_coding_errors(self, tmp_path, git_repo):",
     "test_multiple_ideas_in_coding_errors(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_orphan_dirty_target_rolls_back(self, tmp_path, git_repo):",
     "test_orphan_dirty_target_rolls_back(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
    ("test_cleans_errors_txt_on_coding_recovery(self, tmp_path, git_repo):",
     "test_cleans_errors_txt_on_coding_recovery(self, tmp_path):\n        git_repo = tmp_path / \"target\"\n        script_repo = tmp_path / \"script\""),
]

for old_sig, new_sig in tests_to_fix:
    content = replace_or_fail(old_sig, new_sig, content)

content = content.replace("sr, tr = self._setup(tmp_path, git_repo)", "sr, tr = self._setup(tmp_path)")

# Also, change `tmp_path / "perf-logs"` to `script_repo / "perf-logs"` and similarly for `ideas/` in those tests
content = re.sub(r'\(tmp_path / "perf-logs"', r'(script_repo / "perf-logs"', content)
content = re.sub(r'\(tmp_path / "ideas"', r'(script_repo / "ideas"', content)

with open(file_path, "w") as f:
    f.write(content)

print("Patch applied successfully.")
