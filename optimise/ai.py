# optimise/ai.py
"""AI provider routing with failover between claude and gemini CLIs."""
import os
import subprocess
import shutil
import sys
import time
import random
import logging

log = logging.getLogger("optimiser")

PROVIDERS = {
    "claude": {
        "cmd_text": lambda model: [
            "claude", "--print", "--model", model,
            "--dangerously-skip-permissions", "--verbose",
        ],
        "cmd_edit": lambda model: [
            "claude", "--print", "--model", model,
            "--dangerously-skip-permissions", "--verbose",
            "--allowedTools", "Read", "Edit",
        ],
        "env_cleanup": ["CLAUDECODE"],
        "models": {"best": "opus", "normal": "sonnet"},
        "uses_stdin": True,
        "version_cmd": ["claude", "--version"],
        "version_parse": lambda s: s.split()[0],  # "2.1.76 (Claude Code)" -> "2.1.76"
        "built_with": "2.1.81",
    },
    "gemini": {
        "cmd_text": lambda model: [
            "gemini", "--model", model,
            "-p", "Follow the instructions in the provided text.",
        ],
        "cmd_edit": lambda model: [
            "gemini", "--model", model, "--approval-mode=yolo",
            "-p", "Follow the instructions in the provided text.",
        ],
        "env_cleanup": [],
        "models": {"best": "pro", "normal": "flash"},
        "uses_stdin": True,
        "version_cmd": ["gemini", "--version"],
        "version_parse": lambda s: s.strip(),  # "0.33.1" -> "0.33.1"
        "built_with": "0.34.0",
    },
    "codex": {
        "cmd_text": lambda model: [
            "codex", "exec", "--model", model,
            "--sandbox", "read-only", "-",
        ],
        "cmd_edit": lambda model: [
            "codex", "exec", "--model", model,
            "--dangerously-bypass-approvals-and-sandbox", "-",
        ],
        "env_cleanup": [],
        "models": {"best": "gpt-5.4", "normal": "gpt-5.4-mini"},
        "uses_stdin": True,
        "version_cmd": ["codex", "--version"],
        "version_parse": lambda s: s.split()[-1],  # "codex-cli 0.117.0" -> "0.117.0"
        "built_with": "0.117.0",
    },
}


def get_version(provider_name):
    """Query the installed version of a provider CLI. Returns version string or None."""
    spec = PROVIDERS.get(provider_name)
    if not spec:
        return None
    try:
        result = subprocess.run(
            spec["version_cmd"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return spec["version_parse"](result.stdout)
    except (subprocess.TimeoutExpired, OSError, IndexError, ValueError):
        pass
    return None


class AIRouter:
    """Routes AI calls to claude/gemini with failover."""

    def __init__(self, providers=None, disabled_providers=None,
                 providers_retry_limit=0):
        available = []
        self.version_warnings = {}  # provider -> warning message
        permanently_disabled = set(disabled_providers or [])

        for name in (providers or ["claude", "gemini", "codex"]):
            if name in permanently_disabled:
                log.info(f"AI provider permanently disabled by settings: {name}")
                continue
            if name not in PROVIDERS:
                log.warning(f"Unknown AI provider: {name}")
                continue
            binary = PROVIDERS[name]["cmd_text"]("dummy")[0]
            if shutil.which(binary):
                available.append(name)
                log.info(f"AI provider available: {name}")
                self._check_version(name)
            else:
                log.warning(f"AI provider permanently disabled (not found): {name} ({binary})")
                permanently_disabled.add(name)
        if not available:
            log.error("No AI providers available (all uninstalled or permanently disabled in settings)")
            sys.exit(1)
        self.permanently_disabled = permanently_disabled
        self.available_providers = list(available)
        self.providers = list(available)
        self._last_call_finish_time = {name: 0 for name in available}
        self.providers_retry_limit = providers_retry_limit

    def _check_version(self, name):
        """Compare installed version against built_with and warn on mismatch."""
        spec = PROVIDERS[name]
        built = spec["built_with"]
        installed = get_version(name)
        if installed is None:
            log.warning(f"Could not determine {name} CLI version")
            return
        if installed != built:
            msg = (f"{name} CLI version mismatch: script built with "
                   f"{built} but {installed} is installed")
            self.version_warnings[name] = msg
            log.warning(msg)

    def reset_providers(self):
        self.providers = list(self.available_providers)

    def disable_provider(self, name):
        if name in self.providers:
            self.providers.remove(name)
            log.warning(f"AI provider disabled: {name}")

    @property
    def has_providers(self):
        return len(self.providers) > 0

    def call(self, prompt, tier="best", timeout=600, allow_edits=False,
             cwd=None, purpose=None):
        """Call an AI provider with bounded retry on full exhaustion.

        Returns (stdout, exit_code, provider_name).
        """
        retries_used = 0
        while True:
            provider_name = (
                random.choice(self.providers) if self.providers else None
            )

            if provider_name is None:
                if retries_used >= self.providers_retry_limit:
                    log.error("All AI providers failed during this call")
                    return "", 1, None
                retries_used += 1
                log.warning(
                    f"All AI providers exhausted (retry {retries_used}"
                    f"/{self.providers_retry_limit}). Waiting 2 hours..."
                )
                time.sleep(7200)
                self.reset_providers()
                continue

            elapsed = time.time() - self._last_call_finish_time.get(provider_name, 0)
            if elapsed < 60:
                delay = random.uniform(30, 120)
                log.info(f"Cooling off {delay:.0f}s before calling {provider_name} "
                         f"(last call finished {elapsed:.0f}s ago)")
                time.sleep(delay)

            stdout, rc = self._invoke(provider_name, prompt, tier, timeout,
                                      allow_edits, cwd, purpose)
            self._last_call_finish_time[provider_name] = time.time()

            if rc == 0:
                return stdout, rc, provider_name

            log.warning(f"AI: {provider_name} failed (rc={rc})")
            if provider_name in self.version_warnings:
                log.warning(
                    f"{self.version_warnings[provider_name]}. "
                    "If the error persists, consider updating the script by "
                    "showing the error and this warning to a coding agent."
                )
            self.disable_provider(provider_name)

    def _invoke(self, provider_name, prompt, tier, timeout, allow_edits, cwd,
                purpose=None):
        spec = PROVIDERS[provider_name]
        model = spec["models"][tier]

        if allow_edits:
            cmd = spec["cmd_edit"](model)
        else:
            cmd = spec["cmd_text"](model)

        env = os.environ.copy()
        for var in spec["env_cleanup"]:
            env.pop(var, None)

        label = f" for {purpose}" if purpose else ""
        log.info(f"AI: calling {provider_name}/{model}{label} (edits={allow_edits})")

        try:
            kwargs = dict(
                capture_output=True, text=True,
                timeout=timeout, env=env,
            )
            if cwd:
                kwargs["cwd"] = cwd
            if spec["uses_stdin"]:
                kwargs["input"] = prompt
            else:
                cmd.append(prompt)

            result = subprocess.run(cmd, **kwargs)
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            log.error(f"TIMEOUT: {provider_name} exceeded {timeout}s")
            return "", 1
