# tests/test_ai.py
import pytest
from unittest.mock import patch, MagicMock
from optimise.ai import AIRouter


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
