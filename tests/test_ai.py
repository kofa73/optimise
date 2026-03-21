# tests/test_ai.py
import os
import shutil
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from optimise.ai import AIRouter, PROVIDERS, get_version


class TestProviderCommands:
    def test_gemini_text_uses_noninteractive_flag(self):
        cmd = PROVIDERS["gemini"]["cmd_text"]("pro")
        assert "-p" in cmd, "gemini text cmd must use -p for non-interactive mode"

    def test_gemini_edit_uses_noninteractive_flag(self):
        cmd = PROVIDERS["gemini"]["cmd_edit"]("pro")
        assert "-p" in cmd, "gemini edit cmd must use -p for non-interactive mode"


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
            tier="normal",
            timeout=120,
            allow_edits=True,
            cwd=str(tmp_path),
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
            tier="normal",
            timeout=120,
            allow_edits=True,
            cwd=str(tmp_path),
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


class TestGetVersion:
    @patch("subprocess.run")
    def test_get_version_claude(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="2.1.76 (Claude Code)\n", returncode=0)
        assert get_version("claude") == "2.1.76"

    @patch("subprocess.run")
    def test_get_version_gemini(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="0.33.1\n", returncode=0)
        assert get_version("gemini") == "0.33.1"

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
        with patch("time.sleep"):
            mock_run.side_effect = [
                MagicMock(stdout="", returncode=1),
                MagicMock(stdout="", returncode=1),
                MagicMock(stdout="ok", returncode=0),
            ]
            import logging
            with caplog.at_level(logging.WARNING):
                router.call("test", allow_edits=False)
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
        stdout, rc, provider = router.call("test prompt", allow_edits=False)
        assert stdout == "result text"
        assert rc == 0
        assert provider == "claude"

    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_call_disables_on_failure(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="", returncode=1)
        router = AIRouter(providers=["claude", "gemini"])
        # Both will fail; after two failures it should wait
        # We don't want to actually wait 300s in tests, so mock time.sleep
        with patch("time.sleep"):
            # Call with a timeout to prevent infinite loop
            mock_run.side_effect = [
                MagicMock(stdout="", returncode=1),  # first provider fails
                MagicMock(stdout="", returncode=1),  # second provider fails
                MagicMock(stdout="ok", returncode=0),  # retry succeeds
            ]
            stdout, rc, provider = router.call("test", allow_edits=False)
        assert stdout == "ok"
        assert rc == 0
