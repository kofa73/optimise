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
    def test_clear_improvement_passes(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 9.0}, {"user": 9.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert ok
        assert pct == pytest.approx(10.0)

    def test_below_min_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 9.96}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok
        assert "noise" in detail.lower() or "min" in detail.lower()

    def test_regression_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.5}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok

    def test_individual_regression_exceeds_tradeoff_fails(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 8.0}, {"user": 10.5}]  # row 2 regressed 5%, sum improved 7.5%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        # 7.5% improvement >= 2 * 5% regression = 10% -> FAILS tradeoff
        assert not ok

    def test_individual_regression_passes_with_enough_improvement(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 7.0}, {"user": 10.2}]  # row 2 regressed 2%, sum improved 14%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        # 14% >= 2 * 2% = 4% -> PASSES
        assert ok

    def test_zero_tradeoff_ignores_individual_regression(self):
        baseline = [{"user": 10.0}, {"user": 10.0}]
        result = [{"user": 5.0}, {"user": 14.0}]  # row 2 regressed 40%, sum improved 5%
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=0
        )
        assert ok

    def test_no_improvement_fails(self):
        baseline = [{"user": 10.0}]
        result = [{"user": 10.0}]
        ok, pct, detail = evaluate_success(
            baseline, result, min_improvement_pct=0.5, regression_tradeoff=2
        )
        assert not ok
