# tests/test_benchmark.py
import pytest
from optimise.benchmark import parse_bench_output, BenchmarkError


class TestParseBenchOutput:
    def test_single_line_user_only(self):
        rows = parse_bench_output("user=0.561\n")
        assert len(rows) == 1
        assert rows[0]["user"] == pytest.approx(0.561)

    def test_single_line_multiple_labels(self):
        rows = parse_bench_output("user=0.234, cpu=0.051, gpu=0.180\n")
        assert len(rows) == 1
        assert rows[0]["user"] == pytest.approx(0.234)
        assert rows[0]["cpu"] == pytest.approx(0.051)
        assert rows[0]["gpu"] == pytest.approx(0.180)

    def test_multiple_lines(self):
        text = "user=0.561, cpu=5.372\nuser=0.123\nuser=0.234, cpu=0.051, gpu=0.180\n"
        rows = parse_bench_output(text)
        assert len(rows) == 3
        assert rows[0]["user"] == pytest.approx(0.561)
        assert rows[1]["user"] == pytest.approx(0.123)
        assert "cpu" not in rows[1]
        assert rows[2]["gpu"] == pytest.approx(0.180)

    def test_missing_user_raises(self):
        with pytest.raises(BenchmarkError, match="user"):
            parse_bench_output("cpu=0.5\n")

    def test_empty_output_raises(self):
        with pytest.raises(BenchmarkError):
            parse_bench_output("")

    def test_malformed_value_raises(self):
        with pytest.raises(BenchmarkError):
            parse_bench_output("user=abc\n")

    def test_ignores_blank_lines(self):
        text = "user=0.1\n\nuser=0.2\n"
        rows = parse_bench_output(text)
        assert len(rows) == 2

    def test_no_spaces_around_equals(self):
        rows = parse_bench_output("user=0.5,cpu=1.0\n")
        assert rows[0]["user"] == pytest.approx(0.5)
        assert rows[0]["cpu"] == pytest.approx(1.0)

    def test_leading_dot_value(self):
        rows = parse_bench_output("user=.234, cpu=0.051\n")
        assert rows[0]["user"] == pytest.approx(0.234)


from optimise.benchmark import update_element_best, ConvergenceState


class TestUpdateElementBest:
    def test_first_run_sets_best(self):
        rows = [{"user": 0.5, "cpu": 1.0}, {"user": 0.3}]
        best = update_element_best(None, rows)
        assert best[0]["user"] == pytest.approx(0.5)
        assert best[0]["cpu"] == pytest.approx(1.0)
        assert best[1]["user"] == pytest.approx(0.3)

    def test_keeps_minimum(self):
        best = [{"user": 0.5, "cpu": 1.0}, {"user": 0.3}]
        new = [{"user": 0.4, "cpu": 1.1}, {"user": 0.35}]
        result = update_element_best(best, new)
        assert result[0]["user"] == pytest.approx(0.4)  # improved
        assert result[0]["cpu"] == pytest.approx(1.0)    # kept old
        assert result[1]["user"] == pytest.approx(0.3)   # kept old

    def test_wrong_row_count_raises(self):
        best = [{"user": 0.5}]
        new = [{"user": 0.4}, {"user": 0.3}]
        with pytest.raises(BenchmarkError, match="row"):
            update_element_best(best, new)


class TestConvergence:
    def test_initial_state(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        assert state.tail_counter == 0
        assert state.reference_sum is None

    def test_first_update_sets_reference(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        assert state.reference_sum == pytest.approx(10.0)
        assert state.tail_counter == 0
        assert not state.converged

    def test_significant_improvement_resets_tail(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        state.update(10.0)  # no change, tail=1
        state.update(9.5)   # big drop, reset
        assert state.tail_counter == 0
        assert state.reference_sum == pytest.approx(9.5)

    def test_converges_after_tail_runs(self):
        state = ConvergenceState(threshold_pct=0.1, tail_runs=3)
        state.update(10.0)
        state.update(10.0)  # tail=1
        state.update(10.0)  # tail=2
        state.update(10.0)  # tail=3
        assert state.converged

    def test_tiny_improvement_counts_as_tail(self):
        state = ConvergenceState(threshold_pct=1.0, tail_runs=2)
        state.update(10.0)
        state.update(9.95)  # 0.5% < 1.0% threshold -> tail=1
        state.update(9.94)  # still < 1.0% from reference -> tail=2
        assert state.converged


from optimise.benchmark import evaluate_success


class TestEvaluateSuccess:
    # --- overall mode (default) ---

    def test_overall_clear_improvement_passes(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 9.0}, {"user": 9.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert ok
        assert pct == pytest.approx(10.0)

    def test_overall_below_min_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 9.96}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok
        assert "minimum" in detail.lower() or "below" in detail.lower()

    def test_overall_regression_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.5}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok

    def test_overall_instance_regression_exceeds_cap_fails(self):
        """Guard: any instance regressing > max_regression_pct fails."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.5}]  # row 2: 5% regression > 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok
        assert "regress" in detail.lower()

    def test_overall_instance_regression_within_cap_passes(self):
        """Guard: instance regressing <= max_regression_pct is OK."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.2}]  # row 2: 2% regression <= 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert ok

    def test_overall_no_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
        )
        assert not ok

    # --- instance mode ---

    def test_instance_target_improves_enough_passes(self):
        """Target: the targeted instance must improve by min_improvement_pct."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 10.0}, {"user": 9.0}]   # instance 1: 10% improvement
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert ok
        assert pct == pytest.approx(10.0)  # improvement of targeted instance

    def test_instance_target_not_improved_fails(self):
        """Target: targeted instance barely improved -> fail."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 9.96}]  # instance 1: only 0.4%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert not ok

    def test_instance_sum_regression_exceeds_cap_fails(self):
        """Guard: sum(user) must not regress > max_regression_pct."""
        baseline = [{"user": 5.0}, {"user": 5.0}]   # sum=10
        result = [{"user": 8.0}, {"user": 4.0}]     # sum=12 -> sum regressed 20% > 3%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert not ok
        assert "regress" in detail.lower()

    def test_instance_sum_regression_within_cap_passes(self):
        """Guard: sum(user) regressing <= max_regression_pct is OK."""
        baseline = [{"user": 5.0}, {"user": 5.0}]   # sum=10
        result = [{"user": 5.1}, {"user": 4.0}]     # sum=9.1, sum improved 9%. inst 1 improved 20%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, max_regression_pct=3,
            targeting_mode="least_improved_instance", target_instance_index=1,
        )
        assert ok


from optimise.benchmark import find_least_improved_instance


class TestFindLeastImprovedInstance:
    def test_finds_least_improved(self):
        baseline = [{"user": 10.0}, {"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 8.0},  {"user": 9.5},  {"user": 7.0}]
        # improvements: 20%, 5%, 30% → least improved = index 1
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 1
        assert result["baseline_user"] == pytest.approx(10.0)
        assert result["current_user"] == pytest.approx(9.5)
        assert result["improvement_pct"] == pytest.approx(5.0)

    def test_negative_improvement_selected(self):
        """A regressed instance has negative improvement and is the worst."""
        baseline = [{"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 9.0},  {"user": 11.0}]
        # improvements: 10%, -10% → least improved = index 1
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 1
        assert result["improvement_pct"] == pytest.approx(-10.0)

    def test_all_same_picks_first(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        current  = [{"user": 9.0},  {"user": 9.0}]
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 0  # tied, first wins

    def test_single_row(self):
        baseline = [{"user": 10.0}]
        current  = [{"user": 9.0}]
        result = find_least_improved_instance(baseline, current)
        assert result["index"] == 0
        assert result["improvement_pct"] == pytest.approx(10.0)


from optimise.benchmark import format_perf_log, parse_perf_log


class TestFormatPerfLog:
    def test_basic_format(self):
        rows = [
            {"user": 0.551, "cpu": 5.372},
            {"user": 0.123},
            {"user": 0.234, "cpu": 0.051, "gpu": 0.180},
        ]
        text = format_perf_log(rows)
        assert "# Individual timings" in text
        assert "# Totals" in text
        assert "# Averages" in text
        assert "| user | cpu | gpu |" in text
        # Check totals: user=0.908, cpu=5.423, gpu=0.180
        assert "0.908" in text
        assert "5.423" in text

    def test_single_row(self):
        rows = [{"user": 1.5}]
        text = format_perf_log(rows)
        assert "| user |" in text
        assert "1.5" in text or "1.500" in text

    def test_averages_exclude_missing(self):
        rows = [
            {"user": 1.0, "cpu": 4.0},
            {"user": 2.0},
        ]
        text = format_perf_log(rows)
        # Average of user: (1.0+2.0)/2 = 1.5
        # Average of cpu: 4.0/1 = 4.0 (only 1 row has cpu)
        assert "1.5" in text or "1.500" in text


class TestParsePerfLog:
    def test_round_trip(self):
        rows = [{"user": 0.551, "cpu": 5.372}, {"user": 0.123}]
        text = format_perf_log(rows)
        parsed = parse_perf_log(text)
        assert len(parsed) == 2
        assert parsed[0]["user"] == pytest.approx(0.551)
        assert parsed[0]["cpu"] == pytest.approx(5.372)
        assert parsed[1]["user"] == pytest.approx(0.123)
        assert "cpu" not in parsed[1]


from optimise.runner import run_benchmark_loop


class TestEarlyAbortInstanceMode:
    def test_early_abort_on_instance_regression(self, tmp_path):
        """In instance mode, abort if targeted instance exceeds tolerance."""
        bench = tmp_path / "bench.sh"
        # Instance 0 is fine, instance 1 (targeted) regresses badly
        bench.write_text("#!/bin/sh\necho 'user=9.0'\necho 'user=12.0'\n")
        bench.chmod(0o755)
        with pytest.raises(BenchmarkError, match="early abort"):
            run_benchmark_loop(
                str(bench), cwd=str(tmp_path),
                baseline_user_sum=20.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
                target_instance_index=1,
                target_instance_baseline=10.0,
            )

    def test_early_abort_on_sum_in_instance_mode(self, tmp_path):
        """In instance mode, also abort if sum exceeds tolerance."""
        bench = tmp_path / "bench.sh"
        # Instance 1 (targeted) improved, but sum is way worse
        bench.write_text("#!/bin/sh\necho 'user=19.0'\necho 'user=9.0'\n")
        bench.chmod(0o755)
        with pytest.raises(BenchmarkError, match="early abort"):
            run_benchmark_loop(
                str(bench), cwd=str(tmp_path),
                baseline_user_sum=20.0,
                num_warmup=0,
                convergence_threshold_pct=0.1,
                convergence_tail_runs=3,
                early_abort_pct=0.5,
                target_instance_index=1,
                target_instance_baseline=10.0,
            )
