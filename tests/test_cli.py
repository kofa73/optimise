# tests/test_cli.py
import os
import subprocess
import pytest
from unittest.mock import MagicMock
from optimise.cli import (
    do_init, _BuildState, _succeed_idea, _fail_idea,
    _generate_ideas, GenerationResult,
)
from optimise.git import GitRepo
from optimise.benchmark import format_perf_log


class TestInit:
    def test_creates_settings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").exists()
        content = (tmp_path / "settings.conf").read_text()
        assert "target_repo:" in content
        assert "build_cmd:" in content

    def test_creates_instructions(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "instructions.md").exists()

    def test_creates_learnings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "learnings.md").exists()
        content = (tmp_path / "learnings.md").read_text()
        assert "## What works" in content
        assert "## What to avoid" in content

    def test_creates_directories(self, tmp_path):
        do_init(str(tmp_path))
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            assert (tmp_path / d).is_dir()

    def test_idempotent_does_not_overwrite(self, tmp_path):
        do_init(str(tmp_path))
        # Modify settings
        (tmp_path / "settings.conf").write_text("custom content")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom content"

    def test_creates_missing_files_only(self, tmp_path):
        # Create settings but not learnings
        (tmp_path / "settings.conf").write_text("custom")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom"
        assert (tmp_path / "learnings.md").exists()


class TestDoRun:
    def test_exits_on_missing_settings(self, tmp_path):
        """do_run should exit with error if settings.conf is missing."""
        from optimise.cli import do_run
        with pytest.raises(SystemExit):
            do_run(str(tmp_path))

    def test_exits_on_invalid_settings(self, tmp_path):
        """do_run should exit with error if settings are invalid."""
        from optimise.cli import do_run
        (tmp_path / "settings.conf").write_text("# empty config\n")
        with pytest.raises(SystemExit):
            do_run(str(tmp_path))


def _init_git(path):
    """Initialise a git repo at path with an initial commit."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, check=True, capture_output=True)
    (path / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)


def _make_build_state(tmp_path, idea_file="idea.md", idea_subdir="testing"):
    """Create script + target repos and a _BuildState ready for succeed/fail."""
    script = tmp_path / "script"
    target = tmp_path / "target"
    script.mkdir()
    target.mkdir()
    _init_git(script)
    _init_git(target)

    for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
        (script / d).mkdir(parents=True, exist_ok=True)

    # Place idea in the expected subdir
    (script / "ideas" / idea_subdir / idea_file).write_text(
        "Skip zero-speed orders\n\nSkip pixel work when speed is 0."
    )

    # Write a current-best perf log
    baseline = [{"user": 10.0, "cpu": 100.0}]
    (script / "perf-logs" / "current-best-perf.md").write_text(format_perf_log(baseline))

    # Make target dirty so rollback has something to do
    (target / "src.c").write_text("modified")
    subprocess.run(["git", "add", "src.c"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "change"], cwd=target, check=True, capture_output=True)

    settings = {
        "commit_prefix": "perf",
        "min_improvement_pct": 0.5,
        "individual_regression_tradeoff": 2,
    }

    return _BuildState(
        script_repo=str(script),
        target_repo_path=str(target),
        target_git=GitRepo(str(target)),
        script_git=GitRepo(str(script)),
        settings=settings,
        idea_file=idea_file,
        iteration=1,
        consecutive_perf_failures=0,
        start_time=0,
    )


class TestGenerateIdeas:
    def _setup(self, tmp_path):
        """Create script repo with idea directories and a learnings file."""
        script = tmp_path / "script"
        script.mkdir()
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (script / d).mkdir(parents=True)
        (script / "learnings.md").write_text("## What works\n\n## What to avoid\n")
        (script / "instructions.md").write_text("Optimise for speed.\n")
        return str(script)

    def _make_ai(self, outputs):
        """Create a mock AI that returns outputs in order."""
        ai = MagicMock()
        ai.call = MagicMock(side_effect=outputs)
        return ai

    def test_adds_new_ideas(self, tmp_path):
        """Generation produces ideas → added to todo."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("---\nFILENAME: idea-a\nTITLE: Unroll inner loop\nDESCRIPTION:\nUnroll.\n---\n",
             0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        from optimise.state import list_ideas
        assert len(list_ideas(script_repo, "todo")) == 1

    def test_llm_failure_returns_llm_failure(self, tmp_path):
        """LLM fails every call (rc != 0) → LLM_FAILURE."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("", 1, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE

    def test_no_generation_needed_returns_ok(self, tmp_path):
        """If todo already has enough ideas, no generation needed → OK."""
        script_repo = self._setup(tmp_path)
        (tmp_path / "script" / "ideas" / "todo" / "existing.md").write_text("Existing idea\n\nDo this.")
        ai = self._make_ai([])  # should not be called
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        assert ai.call.call_count == 0

    def test_unparseable_output_returns_llm_failure(self, tmp_path):
        """LLM returns gibberish → LLM_FAILURE."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("here is some random text with no structure", 0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE


class TestSucceedIdea:
    def test_no_per_idea_perf_log_file(self, tmp_path):
        s = _make_build_state(tmp_path)
        best = [{"user": 9.0, "cpu": 90.0}]
        _succeed_idea(s, best, improvement_pct=10.0,
                      detail="test", baseline_sum=10.0)
        perf_path = tmp_path / "script" / "perf-logs" / "idea-perf.md"
        assert not perf_path.exists()

    def test_updates_current_best(self, tmp_path):
        s = _make_build_state(tmp_path)
        best = [{"user": 9.0, "cpu": 90.0}]
        _succeed_idea(s, best, improvement_pct=10.0,
                      detail="test", baseline_sum=10.0)
        current = (tmp_path / "script" / "perf-logs" / "current-best-perf.md").read_text()
        assert "9.0" in current

    def test_appends_perf_table_to_idea(self, tmp_path):
        s = _make_build_state(tmp_path)
        best = [{"user": 9.0, "cpu": 90.0}]
        _succeed_idea(s, best, improvement_pct=10.0,
                      detail="test", baseline_sum=10.0)
        idea_content = (tmp_path / "script" / "ideas" / "done" / "idea.md").read_text()
        assert "# Individual timings" in idea_content


class TestFailIdea:
    def test_no_perf_log_file(self, tmp_path):
        s = _make_build_state(tmp_path)
        best = [{"user": 11.0, "cpu": 110.0}]
        _fail_idea(s, "performance regression", bench_rows=best)
        perf_path = tmp_path / "script" / "perf-logs" / "idea-perf.md"
        assert not perf_path.exists()

    def test_appends_perf_table_to_idea(self, tmp_path):
        s = _make_build_state(tmp_path)
        best = [{"user": 11.0, "cpu": 110.0}]
        _fail_idea(s, "performance regression", bench_rows=best)
        idea_content = (tmp_path / "script" / "ideas" / "done" / "idea.md").read_text()
        assert "# Individual timings" in idea_content

    def test_no_perf_table_without_bench_rows(self, tmp_path):
        s = _make_build_state(tmp_path, idea_subdir="coding")
        _fail_idea(s, "build failure")
        idea_content = (tmp_path / "script" / "ideas" / "done" / "idea.md").read_text()
        assert "# Individual timings" not in idea_content
        assert "outcome: build failure" in idea_content

    def test_early_abort_appends_partial_perf_table(self, tmp_path):
        """Early abort rows (single run, no convergence) are still recorded."""
        s = _make_build_state(tmp_path)
        partial = [{"user": 15.0, "cpu": 150.0}]
        _fail_idea(s, "benchmark early abort: Benchmark early abort: "
                   "15.000s vs baseline 10.000s (-50.0%, need 5.0%)",
                   bench_rows=partial)
        idea_content = (tmp_path / "script" / "ideas" / "done" / "idea.md").read_text()
        assert "# Individual timings" in idea_content
        assert "15.0" in idea_content
        assert "15.000s vs baseline 10.000s" in idea_content


class TestNotApplicable:
    """Test that NOT_APPLICABLE LLM response is detected correctly."""

    def test_parse_not_applicable_positive(self):
        from optimise.runner import parse_not_applicable
        assert parse_not_applicable("NOT_APPLICABLE\nCode already changed.") is True
        assert parse_not_applicable("NOT_APPLICABLE") is True
        assert parse_not_applicable("  NOT_APPLICABLE  \nreason") is True

    def test_parse_not_applicable_negative(self):
        from optimise.runner import parse_not_applicable
        assert parse_not_applicable("I have made the edits.") is False
        assert parse_not_applicable("") is False
        assert parse_not_applicable("NOT_APPLICABLE is not the right answer") is False
