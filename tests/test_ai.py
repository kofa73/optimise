# tests/test_ai.py
import os
import shutil
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from optimise.ai import AIRouter, PROVIDERS, PURPOSE_TIERS, get_version


class TestProviderCommands:
    def test_claude_commands_match_expected_shape(self):
        text_cmd = PROVIDERS["claude"]["cmd_text"]("sonnet")
        edit_cmd = PROVIDERS["claude"]["cmd_edit"]("sonnet")

        assert text_cmd == [
            "claude", "--print", "--model", "sonnet",
            "--dangerously-skip-permissions", "--disable-slash-commands",
            "--verbose",
        ]
        assert edit_cmd == [
            "claude", "--print", "--model", "sonnet",
            "--dangerously-skip-permissions", "--disable-slash-commands",
            "--verbose",
            "--allowedTools", "Read", "Edit",
        ]

    def test_gemini_text_uses_noninteractive_flag(self):
        cmd = PROVIDERS["gemini"]["cmd_text"]("pro")
        assert "-p" in cmd, "gemini text cmd must use -p for non-interactive mode"

    def test_gemini_edit_uses_noninteractive_flag(self):
        cmd = PROVIDERS["gemini"]["cmd_edit"]("pro")
        assert "-p" in cmd, "gemini edit cmd must use -p for non-interactive mode"

    def test_gemini_disables_extensions_for_automation(self):
        text_cmd = PROVIDERS["gemini"]["cmd_text"]("pro")
        edit_cmd = PROVIDERS["gemini"]["cmd_edit"]("pro")

        assert text_cmd[:3] == ["gemini", "-e", "noneAtAll"]
        assert edit_cmd[:3] == ["gemini", "-e", "noneAtAll"]

    def test_codex_text_uses_exec_and_sandbox(self):
        cmd = PROVIDERS["codex"]["cmd_text"]("gpt-5.4")
        assert cmd[:2] == ["codex", "exec"], "codex text cmd must use 'codex exec'"
        assert "--model" in cmd
        assert "gpt-5.4" in cmd
        assert "--skip-git-repo-check" in cmd
        assert "--sandbox" in cmd
        assert "read-only" in cmd
        assert cmd[-1] == "-", "trailing '-' for stdin"

    def test_codex_edit_uses_exec_and_bypass(self):
        cmd = PROVIDERS["codex"]["cmd_edit"]("gpt-5.4")
        assert cmd[:2] == ["codex", "exec"], "codex edit cmd must use 'codex exec'"
        assert "--model" in cmd
        assert "gpt-5.4" in cmd
        assert "--skip-git-repo-check" in cmd
        assert "--dangerously-bypass-approvals-and-sandbox" in cmd
        assert cmd[-1] == "-", "trailing '-' for stdin"
        assert "--full-auto" not in cmd

    def test_codex_uses_stdin(self):
        assert PROVIDERS["codex"]["uses_stdin"] is True

    def test_codex_models(self):
        assert PROVIDERS["codex"]["models"]["best"] == "gpt-5.4"
        assert PROVIDERS["codex"]["models"]["normal"] == "gpt-5.4-mini"


class TestPurposeTiers:
    def test_known_purposes_have_expected_tiers(self):
        assert PURPOSE_TIERS == {
            "generating ideas": "best",
            "implementing idea": "best",
            "reviewing code changes": "normal",
            "reviewing learnings": "best",
        }


@pytest.mark.skipif(
    not shutil.which("gemini"),
    reason="gemini CLI not installed",
)
class TestGeminiIntegration:
    """Integration tests that invoke the real gemini CLI."""

    def test_gemini_edits_file_and_exits(self, tmp_path):
        """Gemini should edit a file in non-interactive mode and exit cleanly."""
        target = tmp_path / "greet.py"
        target.write_text("# TODO: make this print hello\n")

        prompt = (
            "Edit the file greet.py so that when executed with `python3 greet.py` "
            "it prints exactly the word hello on a single line and nothing else. "
            "Do not add any other output. The file must contain only what is needed "
            "to print the single word hello."
        )

        router = AIRouter(providers=["gemini"])
        stdout, rc, provider = router.call(
            prompt,
            timeout=120,
            allow_edits=True,
            cwd=str(tmp_path),
            purpose="implementing idea",
        )
        assert rc == 0, f"gemini exited with rc={rc}"

        result = subprocess.run(
            ["python3", str(target)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, f"greet.py failed: {result.stderr}"
        assert result.stdout.strip() == "hello", (
            f"Expected 'hello', got: {result.stdout.strip()!r}"
        )


@pytest.mark.skipif(
    not shutil.which("claude"),
    reason="claude CLI not installed",
)
class TestClaudeIntegration:
    """Integration tests that invoke the real claude CLI."""

    def test_claude_edits_file_and_exits(self, tmp_path):
        """Claude should edit a file and exit cleanly."""
        target = tmp_path / "greet.py"
        target.write_text("# TODO: make this print hello\n")

        prompt = (
            "Edit the file greet.py so that when executed with `python3 greet.py` "
            "it prints exactly the word hello on a single line and nothing else. "
            "Do not add any other output. The file must contain only what is needed "
            "to print the single word hello."
        )

        router = AIRouter(providers=["claude"])
        stdout, rc, provider = router.call(
            prompt,
            timeout=120,
            allow_edits=True,
            cwd=str(tmp_path),
            purpose="implementing idea",
        )
        assert rc == 0, f"claude exited with rc={rc}"

        result = subprocess.run(
            ["python3", str(target)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, f"greet.py failed: {result.stderr}"
        assert result.stdout.strip() == "hello", (
            f"Expected 'hello', got: {result.stdout.strip()!r}"
        )


@pytest.mark.skipif(
    not shutil.which("codex"),
    reason="codex CLI not installed",
)
class TestCodexIntegration:
    """Integration tests that invoke the real codex CLI."""

    def test_codex_edits_file_and_exits(self, tmp_path):
        """Codex should edit a file in non-interactive mode and exit cleanly."""
        target = tmp_path / "greet.py"
        target.write_text("# TODO: make this print hello\n")

        prompt = (
            "Edit the file greet.py so that when executed with `python3 greet.py` "
            "it prints exactly the word hello on a single line and nothing else. "
            "Do not add any other output. The file must contain only what is needed "
            "to print the single word hello."
        )

        router = AIRouter(providers=["codex"])
        stdout, rc, provider = router.call(
            prompt,
            timeout=120,
            allow_edits=True,
            cwd=str(tmp_path),
            purpose="implementing idea",
        )
        assert rc == 0, f"codex exited with rc={rc}"

        result = subprocess.run(
            ["python3", str(target)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, f"greet.py failed: {result.stderr}"
        assert result.stdout.strip() == "hello", (
            f"Expected 'hello', got: {result.stdout.strip()!r}"
        )


class TestGetVersion:
    @patch("subprocess.run")
    def test_get_version_claude(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="2.1.81 (Claude Code)\n", returncode=0)
        assert get_version("claude") == "2.1.81"

    @patch("subprocess.run")
    def test_get_version_gemini(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="0.34.0\n", returncode=0)
        assert get_version("gemini") == "0.34.0"

    @patch("subprocess.run")
    def test_get_version_codex(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="codex-cli 0.117.0\n", returncode=0)
        assert get_version("codex") == "0.117.0"

    @patch("subprocess.run")
    def test_get_version_returns_none_on_failure(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=1)
        assert get_version("claude") is None

    def test_get_version_unknown_provider(self):
        assert get_version("unknown") is None

    @patch("subprocess.run", side_effect=OSError("not found"))
    def test_get_version_returns_none_on_oserror(self, mock_run):
        assert get_version("claude") is None


class TestVersionWarnings:
    @patch("optimise.ai.get_version", return_value="9.9.9")
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_warns_on_version_mismatch(self, mock_which, mock_ver):
        router = AIRouter(providers=["claude"])
        assert "claude" in router.version_warnings
        assert "9.9.9" in router.version_warnings["claude"]
        assert PROVIDERS["claude"]["built_with"] in router.version_warnings["claude"]

    @patch("optimise.ai.get_version")
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_no_warning_when_version_matches(self, mock_which, mock_ver):
        mock_ver.return_value = PROVIDERS["claude"]["built_with"]
        router = AIRouter(providers=["claude"])
        assert "claude" not in router.version_warnings

    @patch("optimise.ai.get_version", return_value=None)
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_no_warning_when_version_unknown(self, mock_which, mock_ver):
        router = AIRouter(providers=["claude"])
        assert "claude" not in router.version_warnings

    @patch("optimise.ai.get_version", return_value="9.9.9")
    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_version_warning_repeated_on_failure(self, mock_run, mock_which,
                                                  mock_ver, caplog):
        router = AIRouter(providers=["claude", "gemini"])
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="", returncode=1),
        ]
        import logging
        with caplog.at_level(logging.WARNING):
            router.call("test", allow_edits=False, purpose="generating ideas")
        assert any("consider updating the script" in r.message for r in caplog.records)


class TestAIRouter:
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_discovers_available_providers(self, mock_which):
        router = AIRouter(providers=["claude"])
        assert router.has_providers

    @patch("shutil.which", return_value=None)
    def test_no_providers_exits(self, mock_which):
        with pytest.raises(SystemExit):
            AIRouter(providers=["claude"])

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_disable_provider(self, mock_which):
        router = AIRouter(providers=["claude"])
        router.disable_provider("claude")
        assert not router.has_providers

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_reset_providers(self, mock_which):
        router = AIRouter(providers=["claude"])
        router.disable_provider("claude")
        router.reset_providers()
        assert router.has_providers

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_disabled_providers_are_permanently_ignored(self, mock_which):
        router = AIRouter(providers=["claude", "gemini"], disabled_providers=["gemini"])
        assert router.providers == ["claude"]
        assert router.permanently_disabled == {"gemini"}
        router.reset_providers()
        assert router.providers == ["claude"]

    @patch("shutil.which", side_effect=lambda x: None if "gemini" in x else "/usr/bin/binary")
    def test_missing_binary_permanently_disables(self, mock_which):
        router = AIRouter(providers=["claude", "gemini"])
        assert router.providers == ["claude"]
        assert "gemini" in router.permanently_disabled

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_all_providers_disabled_exits(self, mock_which, caplog):
        with pytest.raises(SystemExit):
            AIRouter(providers=["claude", "gemini"], disabled_providers=["claude", "gemini"])
        assert "No AI providers available" in caplog.text

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_call_returns_stdout_on_success(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="result text", returncode=0)
        router = AIRouter(providers=["claude"])
        stdout, rc, provider = router.call(
            "test prompt", allow_edits=False, purpose="generating ideas")
        assert stdout == "result text"
        assert rc == 0
        assert provider == "claude"

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_call_requires_purpose(self, mock_which):
        router = AIRouter(providers=["claude"])
        with pytest.raises(TypeError):
            router.call("test prompt", allow_edits=False)

    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_call_rejects_unknown_purpose(self, mock_which):
        router = AIRouter(providers=["claude"])
        with pytest.raises(ValueError, match="Unknown AI call purpose"):
            router.call("test prompt", allow_edits=False, purpose="unknown")

    @patch("optimise.ai.get_version", return_value=None)
    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_call_disables_on_failure(self, mock_run, mock_which, mock_ver):
        router = AIRouter(providers=["claude", "gemini"])
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="", returncode=1),
        ]
        stdout, rc, provider = router.call(
            "test", allow_edits=False, purpose="generating ideas")
        assert stdout == ""
        assert rc == 1
        assert provider is None
        assert mock_run.call_count == 2


class TestProvidersRetryLimit:
    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_retry_limit_zero_fails_after_one_cycle(self, mock_run, mock_which):
        """retry_limit=0: exhaust all providers once, then fail immediately."""
        router = AIRouter(providers=["claude", "gemini"], providers_retry_limit=0)
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="", returncode=1),
        ]
        with patch("time.sleep") as mock_sleep:
            stdout, rc, provider = router.call(
                "test", allow_edits=False, purpose="generating ideas")
        assert stdout == ""
        assert rc == 1
        assert provider is None
        mock_sleep.assert_not_called()

    @patch("optimise.ai.get_version", return_value=None)
    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_retry_limit_two_retries_then_fails(self, mock_run, mock_which,
                                                 mock_ver):
        """retry_limit=2: 3 total cycles (initial + 2 retries), all fail."""
        router = AIRouter(providers=["claude"], providers_retry_limit=2)
        mock_run.return_value = MagicMock(stdout="", returncode=1)
        with patch("time.sleep") as mock_sleep:
            stdout, rc, provider = router.call(
                "test", allow_edits=False, purpose="generating ideas")
        assert stdout == ""
        assert rc == 1
        assert provider is None
        # 2 retries × 1 sleep(7200) each
        sleep_calls = [c for c in mock_sleep.call_args_list if c[0][0] == 7200]
        assert len(sleep_calls) == 2
        # 3 total cycles × 1 provider = 3 invoke calls
        assert mock_run.call_count == 3

    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_retry_limit_success_on_retry(self, mock_run, mock_which):
        """retry_limit=1: first cycle fails, retry succeeds."""
        router = AIRouter(providers=["claude"], providers_retry_limit=1)
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1),   # first cycle: fail
            MagicMock(stdout="ok", returncode=0),  # retry cycle: success
        ]
        with patch("time.sleep") as mock_sleep:
            stdout, rc, provider = router.call(
                "test", allow_edits=False, purpose="generating ideas")
        assert stdout == "ok"
        assert rc == 0
        assert provider == "claude"
        sleep_calls = [c for c in mock_sleep.call_args_list if c[0][0] == 7200]
        assert len(sleep_calls) == 1


class TestCallPurpose:
    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_purpose_appears_in_log(self, mock_run, mock_which, caplog):
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        import logging
        with caplog.at_level(logging.INFO):
            router.call("test", allow_edits=False, purpose="generating ideas")
        assert any("generating ideas" in r.message for r in caplog.records)


class TestRateLimiting:
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_last_call_finish_time_initialized_to_zero(self, mock_which):
        router = AIRouter(providers=["claude"])
        assert router._last_call_finish_time["claude"] == 0

    @patch("shutil.which", return_value="/usr/bin/fake")
    def test_last_call_finish_time_initialized_for_all_providers(self, mock_which):
        router = AIRouter(providers=["claude", "gemini"])
        assert "claude" in router._last_call_finish_time
        assert "gemini" in router._last_call_finish_time
        assert all(t == 0 for t in router._last_call_finish_time.values())

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_no_delay_on_first_call(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        with patch("time.sleep") as mock_sleep:
            router.call("test", allow_edits=False, purpose="generating ideas")
        mock_sleep.assert_not_called()

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_delay_when_last_call_recent(self, mock_run, mock_which):
        """If last call was <60s ago, should sleep 30-120s."""
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        now = 1000.0
        router._last_call_finish_time["claude"] = now - 30  # 30s ago
        with patch("time.time", return_value=now), \
             patch("time.sleep") as mock_sleep, \
             patch("random.uniform", return_value=75.0) as mock_rand:
            router.call("test", allow_edits=False, purpose="generating ideas")
            mock_rand.assert_called_once_with(30, 120)
            mock_sleep.assert_called_once_with(75.0)

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_no_delay_when_last_call_old(self, mock_run, mock_which):
        """If last call was >=60s ago, no delay."""
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        now = 1000.0
        router._last_call_finish_time["claude"] = now - 120  # 120s ago
        with patch("time.time", return_value=now), \
             patch("time.sleep") as mock_sleep:
            router.call("test", allow_edits=False, purpose="generating ideas")
        mock_sleep.assert_not_called()

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_last_call_finish_time_updated_after_call(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        with patch("time.time", return_value=5000.0):
            router.call("test", allow_edits=False, purpose="generating ideas")
        assert router._last_call_finish_time["claude"] == 5000.0

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_delay_logs_message(self, mock_run, mock_which, caplog):
        mock_run.return_value = MagicMock(stdout="ok", returncode=0)
        router = AIRouter(providers=["claude"])
        now = 1000.0
        router._last_call_finish_time["claude"] = now - 10
        import logging
        with patch("time.time", return_value=now), \
             patch("time.sleep"), \
             patch("random.uniform", return_value=60.0), \
             caplog.at_level(logging.INFO):
            router.call("test", allow_edits=False, purpose="generating ideas")
        assert any("cooling off" in r.message.lower() for r in caplog.records)
