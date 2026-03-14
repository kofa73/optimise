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
        state = determine_startup_state(sr, tr)
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
        state = determine_startup_state(sr, tr)
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


from optimise.runner import check_termination, TerminationReason


class TestCheckTermination:
    def test_max_iterations(self):
        reason = check_termination(
            iteration=50, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.MAX_ITERATIONS

    def test_stagnation(self):
        reason = check_termination(
            iteration=10, max_iterations=50,
            consecutive_perf_failures=5, max_consecutive=5,
            start_time=0, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.STAGNATION

    def test_time_limit(self):
        import time
        reason = check_termination(
            iteration=1, max_iterations=50,
            consecutive_perf_failures=0, max_consecutive=5,
            start_time=time.time() - 400 * 60, max_minutes=300, todo_count=5,
        )
        assert reason == TerminationReason.TIME_LIMIT

    def test_no_termination(self):
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
        assert reason == TerminationReason.IDEA_EXHAUSTION
