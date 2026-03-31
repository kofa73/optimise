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

    def test_disabled_providers_parses_comma_separated(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("disabled_providers: claude, gemini\n")
        result = parse_settings(str(f))
        assert result["disabled_providers"] == ["claude", "gemini"]

    def test_disabled_providers_invalid_names_throws_with_line_number(self, tmp_path):
        f = tmp_path / "settings.conf"
        f.write_text("\n\n\ndisabled_providers: fake1, gemini, fake2\n")
        with pytest.raises(SettingsError) as exc:
            parse_settings(str(f))
        assert "Line 4: Unknown provider(s) in disabled_providers: fake1, fake2" in str(exc.value)


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
        bench_img = tmp_path / "bench.NEF"
        bench_img.write_text("raw")
        bench_xmp = tmp_path / "bench.xmp"
        bench_xmp.write_text("<xml/>")
        return {
            "target_repo": str(target),
            "branch": "optimise-test",
            "optimisation_target": "src/main.c",
            "instructions": str(instr),
            "build_cmd": "make",
            "bench_cmd": "python bench.py",
            "quality_cmd": "",
            "min_improvement_pct": "0.5",
            "max_regression_pct": "3",
            "early_abort_pct": "10",
            "num_warmup_iterations": "0",
            "benchmark_convergence_threshold_pct": "0.1",
            "benchmark_convergence_tail_runs": "5",
            "max_retries": "5",
            "max_iterations": "50",
            "max_consecutive_perf_failures": "5",
            "max_runtime_minutes": "300",
            "idea_generation_batch_size": "5",
            "commit_prefix": "perf",
            "bench_image": str(bench_img),
            "bench_sidecar": str(bench_xmp),
            "module_name": "diffuse",
        }

    def test_valid_settings_pass(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["target_repo"] == settings["target_repo"]
        # Numeric values are converted
        assert result["min_improvement_pct"] == 0.5
        assert result["max_retries"] == 5
        assert result["idea_generation_batch_size"] == 5

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

    def test_early_abort_pct_parsed_as_float(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["early_abort_pct"] = "3.5"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["early_abort_pct"] == 3.5

    def test_early_abort_pct_defaults_to_min_improvement_pct(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        del settings["early_abort_pct"]
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["early_abort_pct"] == result["min_improvement_pct"]

    def test_llm_timeout_parsed_as_int(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["llm_timeout"] = "300"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["llm_timeout"] == 300

    def test_llm_timeout_defaults_to_3600(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        # Don't set llm_timeout — should default to 3600
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["llm_timeout"] == 3600

    def test_llm_timeout_invalid_raises(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["llm_timeout"] = "not_a_number"
        with pytest.raises(SettingsError, match="llm_timeout"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_llm_timeout_in_template(self):
        from optimise.settings import SETTINGS_TEMPLATE
        assert "llm_timeout: 3600" in SETTINGS_TEMPLATE

    def test_max_regression_pct_parsed_as_float(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["max_regression_pct"] = "5.5"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["max_regression_pct"] == 5.5

    def test_max_regression_pct_defaults_to_3(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        del settings["max_regression_pct"]
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["max_regression_pct"] == 3

    def test_targeting_mode_defaults_to_overall(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["targeting_mode"] == "overall"

    def test_targeting_mode_least_improved_valid(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["targeting_mode"] = "least_improved_instance"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["targeting_mode"] == "least_improved_instance"

    def test_targeting_mode_invalid_raises(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["targeting_mode"] = "bogus"
        with pytest.raises(SettingsError, match="targeting_mode"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_old_regression_tradeoff_raises_migration_error(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["individual_regression_tradeoff"] = "2"
        with pytest.raises(SettingsError, match="individual_regression_tradeoff.*max_regression_pct"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_providers_retry_limit_parsed_as_int(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["providers_retry_limit"] = "5"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["providers_retry_limit"] == 5

    def test_providers_retry_limit_defaults_to_0(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["providers_retry_limit"] == 0

    def test_providers_retry_limit_in_template(self):
        from optimise.settings import SETTINGS_TEMPLATE
        assert "providers_retry_limit:" in SETTINGS_TEMPLATE

    def test_bench_image_validated_as_existing_file(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        img = tmp_path / "test.NEF"
        img.write_text("raw")
        settings["bench_image"] = str(img)
        settings["bench_sidecar"] = str(tmp_path / "test.xmp")
        (tmp_path / "test.xmp").write_text("<xml/>")
        settings["module_name"] = "diffuse"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["bench_image"] == str(img)

    def test_bench_image_missing_file_raises(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        settings["bench_image"] = "nonexistent.NEF"
        settings["bench_sidecar"] = "nonexistent.xmp"
        settings["module_name"] = "diffuse"
        with pytest.raises(SettingsError, match="bench_image"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_bench_sidecar_missing_file_raises(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        img = tmp_path / "test.NEF"
        img.write_text("raw")
        settings["bench_image"] = str(img)
        settings["bench_sidecar"] = "nonexistent.xmp"
        settings["module_name"] = "diffuse"
        with pytest.raises(SettingsError, match="bench_sidecar"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_module_name_validated_against_known_modules(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        img = tmp_path / "test.NEF"
        img.write_text("raw")
        sidecar = tmp_path / "test.xmp"
        sidecar.write_text("<xml/>")
        settings["bench_image"] = str(img)
        settings["bench_sidecar"] = str(sidecar)
        settings["module_name"] = "unknown_module"
        with pytest.raises(SettingsError, match="module_name"):
            validate_settings(settings, script_repo=str(tmp_path))

    def test_module_name_diffuse_is_valid(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        img = tmp_path / "test.NEF"
        img.write_text("raw")
        sidecar = tmp_path / "test.xmp"
        sidecar.write_text("<xml/>")
        settings["bench_image"] = str(img)
        settings["bench_sidecar"] = str(sidecar)
        settings["module_name"] = "diffuse"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["module_name"] == "diffuse"

    def test_bench_image_relative_path_resolved(self, tmp_path):
        settings = self._make_valid_settings(tmp_path)
        img = tmp_path / "test.NEF"
        img.write_text("raw")
        sidecar = tmp_path / "test.xmp"
        sidecar.write_text("<xml/>")
        settings["bench_image"] = "test.NEF"
        settings["bench_sidecar"] = "test.xmp"
        settings["module_name"] = "diffuse"
        result = validate_settings(settings, script_repo=str(tmp_path))
        assert result["bench_image"] == str(img)
        assert result["bench_sidecar"] == str(sidecar)