# tests/test_cli.py
import os
import subprocess
import pytest
from unittest.mock import MagicMock, patch
import optimise.cli
from optimise.cli import (
    do_init, _BuildState, _succeed_idea, _fail_idea,
    _generate_ideas, GenerationResult, _do_build_test_benchmark,
    do_run,
)
from optimise.runner import StartupState
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
        "early_abort_pct": 0.5,
        "max_regression_pct": 3,
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


def _make_bench_script(tmp_path, output_line):
    """Create a benchmark script that outputs a single user/cpu line."""
    script = tmp_path / "bench.sh"
    script.write_text(f"#!/bin/sh\necho '{output_line}'\n")
    script.chmod(0o755)
    return str(script)


def _make_full_build_state(tmp_path, bench_cmd, idea_file="idea.md",
                           min_improvement_pct=0.5, early_abort_pct=0.5,
                           max_regression_pct=3,
                           baseline_user=10.0):
    """Full _BuildState with all benchmark-required settings."""
    script = tmp_path / "script"
    target = tmp_path / "target"
    script.mkdir()
    target.mkdir()
    _init_git(script)
    _init_git(target)

    for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
        (script / d).mkdir(parents=True, exist_ok=True)

    (script / "ideas" / "testing" / idea_file).write_text(
        "Test idea\n\nDescription."
    )

    baseline = [{"user": baseline_user, "cpu": baseline_user * 10}]
    from optimise.benchmark import format_perf_log
    (script / "perf-logs" / "current-best-perf.md").write_text(format_perf_log(baseline))

    (target / "src.c").write_text("modified")
    subprocess.run(["git", "add", "src.c"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "change"], cwd=target, check=True, capture_output=True)

    settings = {
        "commit_prefix": "perf",
        "min_improvement_pct": min_improvement_pct,
        "early_abort_pct": early_abort_pct,
        "max_regression_pct": max_regression_pct,
        "num_warmup_iterations": 0,
        "benchmark_convergence_threshold_pct": 0.1,
        "benchmark_convergence_tail_runs": 3,
        "bench_cmd": bench_cmd,
        "quality_cmd": "",
        "commit_scope": ["src/"],
        "bench_image": "/tmp/test.NEF",
        "bench_sidecar": "/tmp/test.xmp",
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
        skip_build=True,
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
            directory=script_repo, settings={"idea_generation_batch_size": 1, "llm_timeout": 600},
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
            directory=script_repo, settings={"idea_generation_batch_size": 1, "llm_timeout": 600},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE

    def test_batch_size_zero_returns_ok(self, tmp_path):
        """If idea_generation_batch_size is 0, no generation needed → OK."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([])  # should not be called
        result = _generate_ideas(
            directory=script_repo, settings={"idea_generation_batch_size": 0, "llm_timeout": 600},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        assert ai.call.call_count == 0

    def test_llm_timeout_passed_to_ai_call(self, tmp_path):
        """ai.call() receives timeout from settings."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("---\nFILENAME: idea-a\nTITLE: Unroll inner loop\nDESCRIPTION:\nUnroll.\n---\n",
             0, "test-provider"),
        ])
        _generate_ideas(
            directory=script_repo, settings={"idea_generation_batch_size": 1, "llm_timeout": 120},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        ai.call.assert_called_once()
        _, kwargs = ai.call.call_args
        assert kwargs["timeout"] == 120

    def test_purpose_passed_to_ai_call(self, tmp_path):
        """ai.call() receives purpose='generating ideas'."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("---\nFILENAME: idea-a\nTITLE: Unroll inner loop\nDESCRIPTION:\nUnroll.\n---\n",
             0, "test-provider"),
        ])
        _generate_ideas(
            directory=script_repo, settings={"idea_generation_batch_size": 1, "llm_timeout": 600},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        ai.call.assert_called_once()
        _, kwargs = ai.call.call_args
        assert kwargs["purpose"] == "generating ideas"

    def test_unparseable_output_returns_llm_failure(self, tmp_path):
        """LLM returns gibberish → LLM_FAILURE."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("here is some random text with no structure", 0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"idea_generation_batch_size": 1, "llm_timeout": 600},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE

    def test_ideas_have_ordinal_prefixes(self, tmp_path):
        """Generated ideas get ordinal prefixes reflecting LLM output order."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("---\nFILENAME: best-idea\nTITLE: Best optimisation\nDESCRIPTION:\nBig win.\n---\n"
             "---\nFILENAME: ok-idea\nTITLE: Average optimisation\nDESCRIPTION:\nSmall win.\n---\n",
             0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"idea_generation_batch_size": 2, "llm_timeout": 600},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        from optimise.state import list_ideas
        ideas = list_ideas(script_repo, "todo")
        assert len(ideas) == 2
        # First idea (best) gets 001-, second gets 002-
        assert ideas[0].startswith("001-"), f"Expected 001- prefix, got: {ideas[0]}"
        assert ideas[1].startswith("002-"), f"Expected 002- prefix, got: {ideas[1]}"


class TestDoReview:
    def test_llm_timeout_passed_to_ai_call(self, tmp_path):
        """_do_review passes timeout from settings to ai.call()."""
        from optimise.cli import _do_review
        script = tmp_path / "script"
        script.mkdir()
        _init_git(script)
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (script / d).mkdir(parents=True)
        (script / "learnings.md").write_text("## What works\n")
        (script / "instructions.md").write_text("Optimise.\n")
        # Place a done idea so _do_review has something to review
        (script / "ideas" / "done" / "idea.md").write_text("Title\n\nBody")
        script_git = GitRepo(str(script))

        ai = MagicMock()
        ai.call = MagicMock(return_value=("review output", 0, "test-provider"))

        _do_review(str(script), script_git, ai, "Optimise.", str(tmp_path),
                   settings={"llm_timeout": 90})
        ai.call.assert_called_once()
        _, kwargs = ai.call.call_args
        assert kwargs["timeout"] == 90

    def test_purpose_passed_to_ai_call(self, tmp_path):
        """_do_review passes purpose='reviewing learnings' to ai.call()."""
        from optimise.cli import _do_review
        script = tmp_path / "script"
        script.mkdir()
        _init_git(script)
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (script / d).mkdir(parents=True)
        (script / "learnings.md").write_text("## What works\n")
        (script / "instructions.md").write_text("Optimise.\n")
        (script / "ideas" / "done" / "idea.md").write_text("Title\n\nBody")
        script_git = GitRepo(str(script))

        ai = MagicMock()
        ai.call = MagicMock(return_value=("review output", 0, "test-provider"))

        _do_review(str(script), script_git, ai, "Optimise.", str(tmp_path),
                   settings={"llm_timeout": 90})
        ai.call.assert_called_once()
        _, kwargs = ai.call.call_args
        assert kwargs["purpose"] == "reviewing learnings"


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


    def test_target_not_reached_increments_consecutive_perf_failures(self, tmp_path):
        """'target not reached' counts toward stagnation."""
        s = _make_build_state(tmp_path)
        best = [{"user": 9.95, "cpu": 99.0}]
        result = _fail_idea(s, "target not reached: 9.950s vs baseline 10.000s (-0.5%, need 0.5%)", bench_rows=best)
        assert result["consecutive_perf_failures"] == 1

    def test_early_abort_does_not_increment_consecutive_perf_failures(self, tmp_path):
        """'benchmark early abort: ...' does NOT count toward stagnation."""
        s = _make_build_state(tmp_path)
        partial = [{"user": 15.0, "cpu": 150.0}]
        result = _fail_idea(s, "benchmark early abort: Benchmark early abort: "
                   "15.000s vs baseline 10.000s (-50.0%, need 5.0%)",
                   bench_rows=partial)
        assert result["consecutive_perf_failures"] == 0


class TestDoBuildTestBenchmarkPerfTable:
    """Integration tests: perf table is written for ALL ideas that run a benchmark."""

    def _idea_content(self, tmp_path):
        done = list((tmp_path / "script" / "ideas" / "done").iterdir())
        assert len(done) == 1
        return done[0].read_text()

    def test_early_abort_idea_has_perf_table(self, tmp_path):
        """Early abort (first run doesn't meet early_abort_pct) → perf table in done idea."""
        # baseline=10.0, bench outputs 10.05 (regression) → early abort triggers
        bench = _make_bench_script(tmp_path, "user=10.05, cpu=100.5")
        s = _make_full_build_state(tmp_path, bench_cmd=bench,
                                   baseline_user=10.0, early_abort_pct=0.5)
        _do_build_test_benchmark(s, retries_left=0)
        content = self._idea_content(tmp_path)
        assert "# Individual timings" in content
        assert "outcome: benchmark early abort:" in content

    def test_target_not_reached_idea_has_perf_table(self, tmp_path):
        """Benchmark converges but result < min_improvement_pct → perf table in done idea."""
        # baseline=10.0, bench improves by 0.3% → passes early_abort (0.1%) but not min (2%)
        bench = _make_bench_script(tmp_path, "user=9.97, cpu=99.7")
        s = _make_full_build_state(tmp_path, bench_cmd=bench,
                                   baseline_user=10.0,
                                   early_abort_pct=0.1,
                                   min_improvement_pct=2.0)
        _do_build_test_benchmark(s, retries_left=0)
        content = self._idea_content(tmp_path)
        assert "# Individual timings" in content
        assert "outcome: target not reached: 9.970s vs baseline 10.000s (+0.3%, need 2.0%)" in content

    def test_instance_regression_exceeds_cap_has_perf_table(self, tmp_path):
        """Individual row regresses beyond max_regression_pct cap → perf table in done idea."""
        import textwrap
        # Two-row baseline: each row user=5.0 (sum=10.0)
        # Bench result: row1=3.0 (improves), row2=6.9 (regresses 38%)
        # Sum: 9.9 = 1% improvement overall
        # max_regression_pct=2: row 2 regressed 38% > 2% cap → fails guard
        bench = tmp_path / "bench2.sh"
        bench.write_text(textwrap.dedent("""\
            #!/bin/sh
            echo 'user=3.0, cpu=30.0'
            echo 'user=6.9, cpu=69.0'
        """))
        bench.chmod(0o755)
        from optimise.benchmark import format_perf_log
        baseline_two = [{"user": 5.0, "cpu": 50.0}, {"user": 5.0, "cpu": 50.0}]
        # Write the two-row baseline BEFORE creating the build state
        (tmp_path / "baseline_two.md").write_text(format_perf_log(baseline_two))
        s = _make_full_build_state(tmp_path, bench_cmd=str(bench),
                                   baseline_user=10.0,           # initial write (one-row)
                                   early_abort_pct=0.5,          # sum 9.9 < 9.95 → passes
                                   max_regression_pct=2)         # guard cap active
        # Overwrite with two-row baseline so evaluate_success sees two rows matching bench output
        (tmp_path / "script" / "perf-logs" / "current-best-perf.md").write_text(
            format_perf_log(baseline_two))
        _do_build_test_benchmark(s, retries_left=0)
        content = self._idea_content(tmp_path)
        assert "# Individual timings" in content



class TestNotApplicable:
    """Test that NOT_APPLICABLE LLM response is detected correctly."""

    def test_parse_not_applicable_positive(self):
        from optimise.runner import parse_not_applicable
        ok, exp = parse_not_applicable("NOT_APPLICABLE\nCode already changed.")
        assert ok is True
        assert exp == "Code already changed."

        ok, exp = parse_not_applicable("NOT_APPLICABLE")
        assert ok is True
        assert exp == ""

        ok, exp = parse_not_applicable("  NOT_APPLICABLE  \nreason")
        assert ok is True
        assert exp == "reason"

    def test_parse_not_applicable_negative(self):
        from optimise.runner import parse_not_applicable
        ok, exp = parse_not_applicable("I have made the edits.")
        assert ok is False
        assert exp == ""

        ok, exp = parse_not_applicable("")
        assert ok is False
        assert exp == ""

        ok, exp = parse_not_applicable("NOT_APPLICABLE is not the right answer")
        assert ok is False
        assert exp == ""


class TestDoCommand:
    def test_build_runs_build_cmd(self, tmp_path, monkeypatch):
        from optimise.cli import do_command
        import optimise.cli
        
        s = _make_full_build_state(tmp_path, bench_cmd="echo")
        settings_path = tmp_path / "script" / "settings.conf"
        (tmp_path / "script" / "bench.NEF").write_text("raw")
        (tmp_path / "script" / "bench.xmp").write_text("<xml/>")
        settings_path.write_text(f"target_repo: {tmp_path / 'target'}\nbranch: main\ninstructions: instructions.md\nbench_cmd: echo\nbuild_cmd: echo BUILD_RUN\noptimisation_target: src.c\ncommit_scope: src/\nbench_image: bench.NEF\nbench_sidecar: bench.xmp\nmodule_name: diffuse\n")
        (tmp_path / "script" / "instructions.md").write_text("test")

        calls = []
        def mock_run_shell_step(name, cmd, cwd):
            calls.append((name, cmd))
            return True, "ok"
        monkeypatch.setattr(optimise.cli, "run_shell_step", mock_run_shell_step)

        do_command("build", str(tmp_path / "script"))
        assert len(calls) == 1
        assert calls[0][0] == "BUILD"
        assert calls[0][1] == "echo BUILD_RUN"

    def test_test_runs_quality_then_benchmark(self, tmp_path, monkeypatch):
        from optimise.cli import do_command
        import optimise.cli
        
        s = _make_full_build_state(tmp_path, bench_cmd="echo user=1.0, cpu=1.0")
        settings_path = tmp_path / "script" / "settings.conf"
        (tmp_path / "script" / "bench.NEF").write_text("raw")
        (tmp_path / "script" / "bench.xmp").write_text("<xml/>")
        settings_path.write_text(f"target_repo: {tmp_path / 'target'}\nbranch: main\ninstructions: instructions.md\nbuild_cmd: echo BUILD_RUN\nbench_cmd: echo user=1.0, cpu=1.0\nquality_cmd: echo QUALITY_PASS\noptimisation_target: src.c\ncommit_scope: src/\nnum_warmup_iterations: 0\nbenchmark_convergence_threshold_pct: 0.1\nbenchmark_convergence_tail_runs: 5\nearly_abort_pct: 0\nbench_image: bench.NEF\nbench_sidecar: bench.xmp\nmodule_name: diffuse\n")
        (tmp_path / "script" / "instructions.md").write_text("test")

        calls = []
        def mock_run_shell_step(name, cmd, cwd):
            calls.append((name, cmd))
            return True, "ok"
        monkeypatch.setattr(optimise.cli, "run_shell_step", mock_run_shell_step)

        bench_calls = []
        def mock_run_benchmark_loop(*args, **kwargs):
            bench_calls.append(True)
            return [{"user": 1.0, "cpu": 1.0}]
        monkeypatch.setattr(optimise.cli, "run_benchmark_loop", mock_run_benchmark_loop)

        do_command("test", str(tmp_path / "script"))

        assert len(calls) == 2
        assert calls[0][0] == "BUILD"
        assert calls[0][1] == "echo BUILD_RUN"
        assert calls[1][0] == "QUALITY"
        assert len(bench_calls) == 1

    def test_qualitycheck_runs_build_then_quality(self, tmp_path, monkeypatch):
        from optimise.cli import do_command
        import optimise.cli

        s = _make_full_build_state(tmp_path, bench_cmd="echo")
        settings_path = tmp_path / "script" / "settings.conf"
        (tmp_path / "script" / "bench.NEF").write_text("raw")
        (tmp_path / "script" / "bench.xmp").write_text("<xml/>")
        settings_path.write_text(f"target_repo: {tmp_path / 'target'}\nbranch: main\ninstructions: instructions.md\nbench_cmd: echo\nbuild_cmd: echo BUILD_RUN\nquality_cmd: echo QUALITY_RUN\noptimisation_target: src.c\ncommit_scope: src/\nbench_image: bench.NEF\nbench_sidecar: bench.xmp\nmodule_name: diffuse\n")
        (tmp_path / "script" / "instructions.md").write_text("test")
        
        calls = []
        def mock_run_shell_step(name, cmd, cwd):
            calls.append((name, cmd))
            return True, "ok"
        monkeypatch.setattr(optimise.cli, "run_shell_step", mock_run_shell_step)
        
        do_command("qualitycheck", str(tmp_path / "script"))
        
        assert len(calls) == 2
        assert calls[0][0] == "BUILD"
        assert calls[0][1] == "echo BUILD_RUN"
        assert calls[1][0] == "QUALITY"
        assert calls[1][1] == "echo QUALITY_RUN"

    def test_benchmark_runs_build_then_benchmark(self, tmp_path, monkeypatch):
        from optimise.cli import do_command
        import optimise.cli
        
        s = _make_full_build_state(tmp_path, bench_cmd="echo user=1.0, cpu=1.0")
        settings_path = tmp_path / "script" / "settings.conf"
        (tmp_path / "script" / "bench.NEF").write_text("raw")
        (tmp_path / "script" / "bench.xmp").write_text("<xml/>")
        settings_path.write_text(f"target_repo: {tmp_path / 'target'}\nbranch: main\ninstructions: instructions.md\nbuild_cmd: echo BUILD_RUN\nbench_cmd: echo user=1.0, cpu=1.0\nquality_cmd: echo QUALITY_PASS\noptimisation_target: src.c\ncommit_scope: src/\nnum_warmup_iterations: 0\nbenchmark_convergence_threshold_pct: 0.1\nbenchmark_convergence_tail_runs: 5\nearly_abort_pct: 0\nbench_image: bench.NEF\nbench_sidecar: bench.xmp\nmodule_name: diffuse\n")
        (tmp_path / "script" / "instructions.md").write_text("test")

        calls = []
        def mock_run_shell_step(name, cmd, cwd):
            calls.append((name, cmd))
            return True, "ok"
        monkeypatch.setattr(optimise.cli, "run_shell_step", mock_run_shell_step)

        bench_calls = []
        def mock_run_benchmark_loop(*args, **kwargs):
            bench_calls.append(True)
            return [{"user": 1.0, "cpu": 1.0}]
        monkeypatch.setattr(optimise.cli, "run_benchmark_loop", mock_run_benchmark_loop)

        do_command("benchmark", str(tmp_path / "script"))

        assert len(calls) == 1
        assert calls[0][0] == "BUILD"
        assert calls[0][1] == "echo BUILD_RUN"
        assert len(bench_calls) == 1

    def test_test_runs_with_commit_does_not_fail_benchmark(self, tmp_path, monkeypatch):
        from optimise.cli import do_command
        import optimise.cli

        s = _make_full_build_state(tmp_path, bench_cmd="echo user=1.0, cpu=1.0")
        settings_path = tmp_path / "script" / "settings.conf"
        (tmp_path / "script" / "bench.NEF").write_text("raw")
        (tmp_path / "script" / "bench.xmp").write_text("<xml/>")
        settings_path.write_text(f"target_repo: {tmp_path / 'target'}\nbranch: main\ninstructions: instructions.md\nbuild_cmd: echo BUILD_RUN\nbench_cmd: echo user=1.0, cpu=1.0\nquality_cmd: echo QUALITY_PASS\noptimisation_target: src/src.c\ncommit_scope: src/\nnum_warmup_iterations: 0\nbenchmark_convergence_threshold_pct: 0.1\nbenchmark_convergence_tail_runs: 5\nearly_abort_pct: 0\nbench_image: bench.NEF\nbench_sidecar: bench.xmp\nmodule_name: diffuse\n")
        (tmp_path / "script" / "instructions.md").write_text("test")
        
        calls = []
        def mock_run_shell_step(name, cmd, cwd):
            calls.append((name, cmd))
            return True, "ok"
        monkeypatch.setattr(optimise.cli, "run_shell_step", mock_run_shell_step)
        
        bench_calls = []
        def mock_run_benchmark_loop(*args, **kwargs):
            bench_calls.append(True)
            return [{"user": 1.0, "cpu": 1.0}]
        monkeypatch.setattr(optimise.cli, "run_benchmark_loop", mock_run_benchmark_loop)
        
        target = tmp_path / "target"
        (target / "src").mkdir()
        (target / "src" / "src.c").write_text("old content")
        subprocess.run(["git", "add", "src/src.c"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=target, check=True)
        
        (target / "src" / "src.c").write_text("new content with different length")
        subprocess.run(["git", "add", "src/src.c"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-m", "new"], cwd=target, check=True)
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=target, check=True, capture_output=True).stdout.decode().strip()

        
        subprocess.run(["git", "reset", "--hard", "HEAD~1"], cwd=target, check=True)
        
        # do_command should complete without SystemExit — the dirty check must
        # only run once, before fetching file contents, not again inside the
        # recursive benchmark call.
        do_command("test", str(tmp_path / "script"), commit=commit)
        
        assert len(calls) == 2
        assert len(bench_calls) == 1


class TestCodingFailureRevertsScope:
    """When AI fails during coding, partial edits in commit_scope must be reverted."""

    def _setup_repos(self, tmp_path):
        """Create target + script repos ready for the CODE state."""
        target = tmp_path / "target"
        target.mkdir()
        _init_git(target)
        (target / "src").mkdir()
        (target / "src" / "main.c").write_text("original")
        subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init src"], cwd=target,
                        check=True, capture_output=True)

        script = tmp_path / "script"
        script.mkdir()
        _init_git(script)
        for d in ["ideas/todo", "ideas/coding", "ideas/testing",
                   "ideas/done", "perf-logs"]:
            (script / d).mkdir(parents=True, exist_ok=True)
        (script / "ideas" / "coding" / "001-test-idea.md").write_text(
            "Test Idea\n\nModify src/main.c"
        )
        (script / "perf-logs" / "current-best-perf.md").write_text(
            format_perf_log([{"user": 10.0, "cpu": 100.0}])
        )
        (script / "instructions.md").write_text("test instructions")
        (script / "learnings.md").write_text(
            "## What works\n\n## What to avoid\n"
        )
        subprocess.run(["git", "add", "."], cwd=script, check=True,
                        capture_output=True)
        subprocess.run(["git", "commit", "-m", "setup"], cwd=script,
                        check=True, capture_output=True)

        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=target,
            capture_output=True, text=True,
        ).stdout.strip()

        (script / "bench.NEF").write_text("raw")
        (script / "bench.xmp").write_text("<xml/>")
        (script / "settings.conf").write_text(
            f"target_repo: {target}\n"
            f"branch: {branch}\n"
            f"optimisation_target: src/main.c\n"
            f"instructions: instructions.md\n"
            f"build_cmd: true\n"
            f"bench_cmd: echo 'user 10.0 cpu 100.0'\n"
            f"max_retries: 2\n"
            f"max_iterations: 1\n"
            f"max_consecutive_perf_failures: 5\n"
            f"max_runtime_minutes: 60\n"
            f"min_improvement_pct: 0.5\n"
            f"max_regression_pct: 3\n"
            f"num_warmup_iterations: 0\n"
            f"benchmark_convergence_threshold_pct: 1\n"
            f"benchmark_convergence_tail_runs: 3\n"
            f"commit_scope: src/\n"
            f"idea_generation_batch_size: 5\n"
            f"llm_timeout: 60\n"
            f"bench_image: bench.NEF\n"
            f"bench_sidecar: bench.xmp\n"
            f"module_name: diffuse\n"
        )

        return target, script

    def test_reverts_scope_before_retry(self, tmp_path):
        """Partial edits from a failed coding attempt must be reverted
        before the next retry, so the LLM starts from clean state."""
        target, script = self._setup_repos(tmp_path)

        file_states_at_call = []

        def ai_call_side_effect(prompt, **kwargs):
            # Record state of file when AI is invoked
            file_states_at_call.append(
                (target / "src" / "main.c").read_text()
            )
            # Simulate a half-finished edit left by the provider
            (target / "src" / "main.c").write_text("partial edit")
            return ("", 1, "test-provider")

        mock_ai = MagicMock()
        mock_ai.call.side_effect = ai_call_side_effect

        with patch("optimise.cli.AIRouter", return_value=mock_ai), \
             patch("optimise.cli.determine_startup_state",
                   return_value=StartupState.CODE), \
             patch("optimise.cli._do_review"), \
             patch("optimise.cli._generate_ideas",
                   return_value=GenerationResult.OK):
            do_run(str(script))

        # AI called twice (max_retries = 2)
        assert len(file_states_at_call) == 2
        # On the second attempt the file must be clean, not the partial edit
        assert file_states_at_call[1] == "original"


class TestBaselinePreconditions:
    """BASELINE must check commit_scope cleanliness and create perf-logs/."""

    def _setup_repos(self, tmp_path, *, create_perf_logs=True):
        """Create target + script repos ready for BASELINE state."""
        target = tmp_path / "target"
        target.mkdir()
        _init_git(target)
        (target / "src").mkdir()
        (target / "src" / "main.c").write_text("original")
        subprocess.run(["git", "add", "."], cwd=target, check=True,
                        capture_output=True)
        subprocess.run(["git", "commit", "-m", "init src"], cwd=target,
                        check=True, capture_output=True)

        script = tmp_path / "script"
        script.mkdir()
        _init_git(script)
        for d in ["ideas/todo", "ideas/coding", "ideas/testing",
                   "ideas/done"]:
            (script / d).mkdir(parents=True, exist_ok=True)
        if create_perf_logs:
            (script / "perf-logs").mkdir(parents=True, exist_ok=True)
        (script / "instructions.md").write_text("test instructions")
        (script / "learnings.md").write_text(
            "## What works\n\n## What to avoid\n"
        )
        subprocess.run(["git", "add", "."], cwd=script, check=True,
                        capture_output=True)
        subprocess.run(["git", "commit", "-m", "setup"], cwd=script,
                        check=True, capture_output=True)

        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=target,
            capture_output=True, text=True,
        ).stdout.strip()

        (script / "bench.NEF").write_text("raw")
        (script / "bench.xmp").write_text("<xml/>")
        (script / "settings.conf").write_text(
            f"target_repo: {target}\n"
            f"branch: {branch}\n"
            f"optimisation_target: src/main.c\n"
            f"instructions: instructions.md\n"
            f"build_cmd: true\n"
            f"bench_cmd: echo 'user 10.0 cpu 100.0'\n"
            f"max_retries: 2\n"
            f"max_iterations: 1\n"
            f"max_consecutive_perf_failures: 5\n"
            f"max_runtime_minutes: 60\n"
            f"min_improvement_pct: 0.5\n"
            f"max_regression_pct: 3\n"
            f"num_warmup_iterations: 0\n"
            f"benchmark_convergence_threshold_pct: 1\n"
            f"benchmark_convergence_tail_runs: 3\n"
            f"commit_scope: src/\n"
            f"idea_generation_batch_size: 5\n"
            f"llm_timeout: 60\n"
            f"bench_image: bench.NEF\n"
            f"bench_sidecar: bench.xmp\n"
            f"module_name: diffuse\n"
        )

        return target, script

    def test_hard_fails_when_commit_scope_dirty(self, tmp_path, monkeypatch):
        """BASELINE must sys.exit(1) if commit_scope has uncommitted changes."""
        target, script = self._setup_repos(tmp_path)
        # Dirty a file in commit_scope
        (target / "src" / "main.c").write_text("dirty")

        # If the dirty check is missing, the build step would be reached.
        # Replace it with something that makes the test fail loudly.
        class _BuildReached(Exception):
            pass
        monkeypatch.setattr(
            optimise.cli, "run_shell_step",
            lambda *a, **kw: (_ for _ in ()).throw(_BuildReached()),
        )

        mock_ai = MagicMock()
        with patch("optimise.cli.AIRouter", return_value=mock_ai), \
             patch("optimise.cli.determine_startup_state",
                   return_value=StartupState.BASELINE):
            with pytest.raises(SystemExit):
                do_run(str(script))

    def test_creates_perf_logs_dir_when_missing(self, tmp_path, monkeypatch):
        """BASELINE must create perf-logs/ if it doesn't exist."""
        target, script = self._setup_repos(tmp_path, create_perf_logs=False)

        monkeypatch.setattr(
            optimise.cli, "run_benchmark_loop",
            lambda *a, **kw: [{"user": 10.0, "cpu": 100.0}],
        )
        mock_ai = MagicMock()
        with patch("optimise.cli.AIRouter", return_value=mock_ai), \
             patch("optimise.cli.determine_startup_state",
                   return_value=StartupState.BASELINE), \
             patch("optimise.cli._generate_ideas",
                   return_value=GenerationResult.OK):
            do_run(str(script))

        assert (script / "perf-logs").is_dir()
        assert (script / "perf-logs" / "baseline-perf.md").exists()
        assert (script / "perf-logs" / "current-best-perf.md").exists()


class TestDoCodeReview:
    """Tests for _do_code_review()."""

    def test_lgtm_returns_true(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("LGTM\n", 0, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "diff --git a/src/main.c\n-old\n+new"
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        approved, feedback = _do_code_review(
            target_git, ai, settings, "Optimise.", "Remove loop\n\nDetails."
        )
        assert approved is True
        assert feedback == ""

    def test_feedback_returns_false_with_feedback(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("Stale comment on line 42.", 0, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "diff --git a/src/main.c\n-old\n+new"
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        approved, feedback = _do_code_review(
            target_git, ai, settings, "Optimise.", "Remove loop\n\nDetails."
        )
        assert approved is False
        assert "Stale comment" in feedback

    def test_llm_failure_returns_true(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("", 1, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "diff --git a/src/main.c\n-old\n+new"
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        approved, feedback = _do_code_review(
            target_git, ai, settings, "Optimise.", "Remove loop\n\nDetails."
        )
        assert approved is True
        assert feedback == ""

    def test_empty_diff_skips_review(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        target_git = MagicMock()
        target_git.diff_scope.return_value = ""
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        approved, feedback = _do_code_review(
            target_git, ai, settings, "Optimise.", "Remove loop\n\nDetails."
        )
        assert approved is True
        assert feedback == ""
        ai.call.assert_not_called()

    def test_uses_normal_tier(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("LGTM", 0, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "some diff"
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        _do_code_review(target_git, ai, settings, "Optimise.", "idea")
        _, kwargs = ai.call.call_args
        assert kwargs["tier"] == "normal"

    def test_passes_llm_timeout(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("LGTM", 0, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "some diff"
        settings = {"commit_scope": ["src/"], "llm_timeout": 120}

        _do_code_review(target_git, ai, settings, "Optimise.", "idea")
        _, kwargs = ai.call.call_args
        assert kwargs["timeout"] == 120

    def test_passes_purpose(self):
        from optimise.cli import _do_code_review
        ai = MagicMock()
        ai.call.return_value = ("LGTM", 0, "test-provider")
        target_git = MagicMock()
        target_git.diff_scope.return_value = "some diff"
        settings = {"commit_scope": ["src/"], "llm_timeout": 60}

        _do_code_review(target_git, ai, settings, "Optimise.", "idea")
        _, kwargs = ai.call.call_args
        assert kwargs["purpose"] == "reviewing code changes"


class TestComputeTarget:
    """_compute_target sets targeting state in settings dict."""

    def _make_sidecar(self, tmp_path):
        """Create a minimal 2-instance XMP sidecar for testing."""
        xmp = tmp_path / "test.xmp"
        xmp.write_text('''\
<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:darktable="http://darktable.sf.net/"
    darktable:iop_order_list="diffuse,0,diffuse,1">
   <darktable:history>
    <rdf:Seq>
     <rdf:li
      darktable:num="0"
      darktable:operation="diffuse"
      darktable:enabled="1"
      darktable:modversion="2"
      darktable:params="0a0000000000000020000000000000000000000000000000000000000000000000000000000000000000003f0000003f0000003f0000003f00000000"
      darktable:multi_name="_builtin_artistic effects | bloom"
      darktable:multi_name_hand_edited="0"
      darktable:multi_priority="0"
      darktable:blendop_version="14"
      darktable:blendop_params=""/>
     <rdf:li
      darktable:num="1"
      darktable:operation="diffuse"
      darktable:enabled="1"
      darktable:modversion="2"
      darktable:params="0b000000000000004000000000008040000000000000a0c00000a0c00000a0c00000a0c000000000000080bf000080bf000080bf000080bf00000000"
      darktable:multi_name="_builtin_lens deblur | hard"
      darktable:multi_name_hand_edited="0"
      darktable:multi_priority="1"
      darktable:blendop_version="14"
      darktable:blendop_params=""/>
    </rdf:Seq>
   </darktable:history>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
''')
        return str(xmp)

    def test_instance_targeting_sets_label_and_params(self, tmp_path):
        """In least_improved_instance mode, stashes label and params."""
        from optimise.benchmark import format_perf_log
        from optimise.cli import _compute_target

        script = tmp_path / "script"
        script.mkdir()
        (script / "perf-logs").mkdir(parents=True)

        baseline = [{"user": 10.0}, {"user": 10.0}]
        current = [{"user": 8.0}, {"user": 9.5}]   # instance 1 least improved
        (script / "perf-logs" / "baseline-perf.md").write_text(format_perf_log(baseline))
        (script / "perf-logs" / "current-best-perf.md").write_text(format_perf_log(current))

        sidecar = self._make_sidecar(tmp_path)
        settings = {
            "targeting_mode": "least_improved_instance",
            "bench_sidecar": sidecar,
            "module_name": "diffuse",
        }

        _compute_target(str(script), settings)

        assert settings["_target_instance_index"] == 1
        assert settings["_target_instance_baseline"] == pytest.approx(10.0)
        assert settings["_target_instance_current"] == pytest.approx(9.5)
        assert settings["_target_instance_label"] == "hard"
        assert settings["_target_instance_params"]["iterations"] == 11
        assert settings["_target_instance_improvement_pct"] == pytest.approx(5.0)
        assert settings["_avg_improvement_pct"] == pytest.approx(12.5)  # (20% + 5%) / 2
        assert len(settings["_all_instances"]) == 2

    def test_overall_mode_clears_all_targeting_state(self, tmp_path):
        """In overall mode, all targeting keys are cleared."""
        from optimise.cli import _compute_target

        settings = {
            "targeting_mode": "overall",
            "_target_instance_index": 1,
            "_target_instance_baseline": 10.0,
            "_target_instance_current": 9.5,
            "_target_instance_label": "bloom",
            "_target_instance_params": {},
            "_target_instance_improvement_pct": 5.0,
            "_avg_improvement_pct": 8.0,
            "_all_instances": [],
        }

        _compute_target(str(tmp_path), settings)

        for key in ("_target_instance_index", "_target_instance_baseline",
                     "_target_instance_current", "_target_instance_label",
                     "_target_instance_params", "_target_instance_improvement_pct",
                     "_avg_improvement_pct", "_all_instances"):
            assert key not in settings


class TestBuildTargetingDict:
    """_build_targeting_dict assembles targeting dict from settings."""

    def test_returns_none_when_overall(self):
        from optimise.cli import _build_targeting_dict
        settings = {"targeting_mode": "overall"}
        assert _build_targeting_dict(settings) is None

    def test_returns_none_when_no_label(self):
        from optimise.cli import _build_targeting_dict
        settings = {"targeting_mode": "least_improved_instance"}
        assert _build_targeting_dict(settings) is None

    def test_returns_dict_when_targeting(self):
        from optimise.cli import _build_targeting_dict
        settings = {
            "targeting_mode": "least_improved_instance",
            "module_name": "diffuse",
            "_target_instance_index": 9,
            "_target_instance_label": "lens deblur | hard",
            "_target_instance_params": {
                "iterations": 10, "sharpness": 0.0, "radius": 512,
                "regularization": 3.0, "variance_threshold": 0.0,
                "anisotropy_first": 5.0, "anisotropy_second": 5.0,
                "anisotropy_third": 5.0, "anisotropy_fourth": 5.0,
                "threshold": 0.0,
                "first": -0.25, "second": -0.25, "third": -0.25, "fourth": -0.25,
                "radius_center": 0,
            },
            "_target_instance_baseline": 9.954,
            "_target_instance_current": 9.745,
            "_target_instance_improvement_pct": 2.1,
            "_avg_improvement_pct": 8.4,
            "_all_instances": [{"label": f"inst{i}"} for i in range(21)],
        }
        result = _build_targeting_dict(settings)
        assert result["module_name"] == "diffuse"
        assert result["instance_count"] == 21
        assert result["index"] == 9
        assert result["label"] == "lens deblur | hard"
        assert result["improvement_pct"] == pytest.approx(2.1)
        assert result["avg_improvement_pct"] == pytest.approx(8.4)
        assert result["baseline_user"] == pytest.approx(9.954)
        assert result["current_user"] == pytest.approx(9.745)
        assert "iterations: 10" in result["params_text"]
