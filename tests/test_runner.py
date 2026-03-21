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
        state = determine_startup_state(sr, tr, {"commit_scope": ["."]})
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
        state = determine_startup_state(sr, tr, {"commit_scope": ["."]})
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

    def test_no_timeout_on_subprocess(self):
        """Shell steps must not impose a timeout."""
        with patch("optimise.runner.subprocess.run", wraps=subprocess.run) as mock_run:
            run_shell_step("TEST", "echo hello", cwd="/tmp")
        for call in mock_run.call_args_list:
            assert "timeout" not in call.kwargs


from optimise.runner import check_termination, TerminationReason


class TestCheckTermination:
    def test_max_iterations(self):
        reason = check_termination(
            iteration=50, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300,
        )
        assert reason == TerminationReason.MAX_ITERATIONS

    def test_stagnation(self):
        reason = check_termination(
            iteration=10, max_iterations=50,
            consecutive_perf_failures=5, max_consecutive=5,
            start_time=0, max_minutes=300,
        )
        assert reason == TerminationReason.STAGNATION

    def test_time_limit(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time() - 400 * 60, max_minutes=300,
        )
        assert reason == TerminationReason.TIME_LIMIT

    def test_no_termination(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time(), max_minutes=300,
        )
        assert reason is None

    def test_empty_todo_does_not_terminate(self):
        """Empty todo is normal after an idea completes — not exhaustion."""
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time(), max_minutes=300,
        )
        assert reason is None


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
            early_abort_pct=0.5,
        )
        assert result is not None
        assert len(result) == 1
        assert result[0]["user"] == pytest.approx(1.0)

    def test_early_abort_on_regression(self, tmp_path):
        """Regression is always worse than improvement threshold → abort."""
        outputs = ["user=3.000\n"]  # way worse than baseline of 2.0
        cmd = self._make_bench_script(tmp_path, outputs)
        with pytest.raises(BenchmarkError) as exc_info:
            run_benchmark_loop(
                bench_cmd=cmd, cwd=str(tmp_path),
                baseline_user_sum=2.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
            )
        assert exc_info.value.rows is not None
        assert exc_info.value.rows[0]["user"] == pytest.approx(3.0)

    def test_early_abort_insufficient_improvement(self, tmp_path):
        """First run shows 3% improvement but early_abort_pct is 10% → abort."""
        # baseline=100, first run=97 (3% improvement), threshold needs <=90
        outputs = ["user=97.000\n"]
        cmd = self._make_bench_script(tmp_path, outputs)
        with pytest.raises(BenchmarkError) as exc_info:
            run_benchmark_loop(
                bench_cmd=cmd, cwd=str(tmp_path),
                baseline_user_sum=100.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=10,
            )
        assert exc_info.value.rows is not None
        assert exc_info.value.rows[0]["user"] == pytest.approx(97.0)

    def test_no_early_abort_when_improvement_meets_threshold(self, tmp_path):
        """First run meets early_abort_pct → no abort, converge."""
        # baseline=100, first run=89 (11% improvement), early_abort_pct=10%
        outputs = ["user=89.000\n"] * 5
        cmd = self._make_bench_script(tmp_path, outputs)
        result = run_benchmark_loop(
            bench_cmd=cmd, cwd=str(tmp_path),
            baseline_user_sum=100.0,
            num_warmup=0,
            convergence_threshold_pct=0.1,
            convergence_tail_runs=3,
            early_abort_pct=10,
        )
        assert result[0]["user"] == pytest.approx(89.0)

    def test_early_abort_uses_early_abort_pct_not_min_improvement_pct(self, tmp_path):
        """early_abort_pct=5, first run improves 7% → NOT aborted.

        Even though 7% < a hypothetical min_improvement_pct=10,
        the early abort only compares against early_abort_pct.
        """
        # baseline=100, first run=93 (7% improvement), early_abort_pct=5% → OK
        outputs = ["user=93.000\n"] * 5
        cmd = self._make_bench_script(tmp_path, outputs)
        result = run_benchmark_loop(
            bench_cmd=cmd, cwd=str(tmp_path),
            baseline_user_sum=100.0,
            num_warmup=0,
            convergence_threshold_pct=0.1,
            convergence_tail_runs=3,
            early_abort_pct=5,
        )
        assert result[0]["user"] == pytest.approx(93.0)

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
            early_abort_pct=0.5,
        )
        assert result[0]["user"] == pytest.approx(1.0)

    def test_no_timeout_on_subprocess_calls(self, tmp_path):
        """Benchmark subprocess calls must not impose a timeout."""
        outputs = ["user=1.000\n"] * 7
        cmd = self._make_bench_script(tmp_path, outputs)
        with patch("optimise.runner.subprocess.run", wraps=subprocess.run) as mock_run:
            run_benchmark_loop(
                bench_cmd=cmd, cwd=str(tmp_path),
                baseline_user_sum=2.0,
                num_warmup=1,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
            )
        for call in mock_run.call_args_list:
            assert "timeout" not in call.kwargs, \
                f"subprocess.run called with timeout={call.kwargs['timeout']}"


from optimise.runner import parse_generated_ideas


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


from optimise.runner import parse_not_applicable


class TestParseNotApplicable:
    def test_parse_not_applicable_positive_with_explanation(self):
        text = "NOT_APPLICABLE\nThis code has already been optimised in a previous step."
        is_na, explanation = parse_not_applicable(text)
        assert is_na is True
        assert explanation == "This code has already been optimised in a previous step."

    def test_parse_not_applicable_positive_no_explanation(self):
        text = "NOT_APPLICABLE"
        is_na, explanation = parse_not_applicable(text)
        assert is_na is True
        assert explanation == ""

    def test_parse_not_applicable_negative(self):
        text = "I have implemented the changes."
        is_na, explanation = parse_not_applicable(text)
        assert is_na is False
        assert explanation == ""

    def test_parse_not_applicable_whitespace(self):
        text = "\n  NOT_APPLICABLE  \n\n  The algorithm changed significantly.  \n"
        is_na, explanation = parse_not_applicable(text)
        assert is_na is True
        assert explanation == "The algorithm changed significantly."


