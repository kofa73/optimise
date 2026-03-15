import pytest
from optimise.settings import parse_settings, validate_settings, SettingsError


class TestParseSettings:
    def test_parses_key_value_pairs(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo: /some/path\nbuild_cmd: make\n")
        result = parse_settings(str(f))
        assert result["target_repo"] == "/some/path"
        assert result["build_cmd"] == "make"

    def test_ignores_comments(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("# this is a comment\ntarget_repo: /path\n")
        result = parse_settings(str(f))
        assert "this" not in result
        assert result["target_repo"] == "/path"

    def test_ignores_blank_lines(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo: /path\n\n\nbuild_cmd: make\n")
        result = parse_settings(str(f))
        assert len(result) == 2

    def test_strips_whitespace_from_values(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("target_repo:   /some/path   \n")
        result = parse_settings(str(f))
        assert result["target_repo"] == "/some/path"

    def test_empty_value(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("quality_cmd:\n")
        result = parse_settings(str(f))
        assert result["quality_cmd"] == ""

    def test_preserves_colons_in_values(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("build_cmd: make -C /path:to:thing\n")
        result = parse_settings(str(f))
        assert result["build_cmd"] == "make -C /path:to:thing"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_settings("/nonexistent/path")


class TestValidateSettings:
    def _make_valid_settings(self, tmp_path):
        """Return a minimal valid settings dict."""
        target = tmp_path / "target"
        target.mkdir()
        src = target / "src" / "main.c"
        src.parent.mkdir(parents=True)
        src.write_text("int main() {}")
        instr = tmp_path / "instructions.md"
        instr.write_text("do stuff")
        return {
            "target_repo": str(target),
            "branch": "optimise-test",
            "optimisation_target": "src/main.c",
            "instructions": str(instr),
            "build_cmd": "make",
            "bench_cmd": "python bench.py",
            "quality_cmd": "",
            "min_improvement_pct": "0.5",
            "individual_regression_tradeoff": "2",
            "early_abort_regression_pct": "10",
            "num_warmup_iterations": "0",
            "benchmark_convergence_threshold_pct": "0.1",
            "benchmark_convergence_tail_runs": "5",
            "max_retries": "5",
            "max_iterations": "50",
            "max_consecutive_perf_failures": "5",
            "max_runtime_minutes": "300",
            "review_frequency": "3",
            "min_ideas": "5",
            "max_dedup_attempts": "10",
            "commit_prefix": "perf",
        }

    def test_valid_settings_pass(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["target_repo"] == settings["target_repo"]
        # Numeric values are converted
        assert result["min_improvement_pct"] == 0.5
        assert result["max_retries"] == 5

    def test_missing_target_repo_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        del settings["target_repo"]
        with pytest.raises(SettingsError, match="target_repo"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_nonexistent_target_repo_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["target_repo"] = "/nonexistent/repo"
        with pytest.raises(SettingsError, match="target_repo"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_missing_build_cmd_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["build_cmd"] = ""
        with pytest.raises(SettingsError, match="build_cmd"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_missing_bench_cmd_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["bench_cmd"] = ""
        with pytest.raises(SettingsError, match="bench_cmd"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_invalid_numeric_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["min_improvement_pct"] = "not_a_number"
        with pytest.raises(SettingsError, match="min_improvement_pct"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_empty_quality_cmd_is_ok(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["quality_cmd"] = ""
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["quality_cmd"] == ""

    def test_nonexistent_optimisation_target_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["optimisation_target"] = "nonexistent.c"
        with pytest.raises(SettingsError, match="optimisation_target"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_comma_separated_targets(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        target = tmp_path / "target"
        (target / "src" / "other.c").write_text("void f() {}")
        settings["optimisation_target"] = "src/main.c, src/other.c"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["optimisation_target"] == ["src/main.c", "src/other.c"]

    def test_single_target_returns_list(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["optimisation_target"] = "src/main.c"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["optimisation_target"] == ["src/main.c"]

    def test_commit_scope_parses_list(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["commit_scope"] = "src/iop/, src/common/"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["commit_scope"] == ["src/iop/", "src/common/"]

    def test_commit_scope_defaults_to_src(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["commit_scope"] == ["src/"]

    def test_nonexistent_instructions_fails(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["instructions"] = "nonexistent.md"
        with pytest.raises(SettingsError, match="instructions"):
            validate_settings(settings, script_repo=str(tmp_path))