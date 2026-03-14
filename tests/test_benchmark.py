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
