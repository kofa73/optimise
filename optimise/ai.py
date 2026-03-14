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
    },
    "gemini": {
        "cmd_text": lambda model: [
            "gemini", "--model", model,
            "Follow the instructions in the provided text.",
        ],
        "cmd_edit": lambda model: [
            "gemini", "--model", model, "--approval-mode=yolo",
            "Follow the instructions in the provided text.",
        ],
        "env_cleanup": [],
        "models": {"best": "pro", "normal": "flash"},
        "uses_stdin": True,
    },
}


class AIRouter:
    """Routes AI calls to claude/gemini with failover."""

    def __init__(self, providers=None):
        available = []
        for name in (providers or ["claude", "gemini"]):
            if name not in PROVIDERS:
                log.warning(f"Unknown AI provider: {name}")
                continue
            binary = PROVIDERS[name]["cmd_text"]("dummy")[0]
            if shutil.which(binary):
                available.append(name)
                log.info(f"AI provider available: {name}")
            else:
                log.warning(f"AI provider not found: {name} ({binary})")
        if not available:
            log.error("No AI providers available")
            sys.exit(1)
        self.available_providers = list(available)
        self.providers = list(available)

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
             cwd=None, provider_override=None):
        """Call an AI provider. Retries indefinitely with wait on full exhaustion.

        Returns (stdout, exit_code, provider_name).
        """
        while True:
            provider_name = provider_override or (
                random.choice(self.providers) if self.providers else None
            )

            if provider_name is None:
                log.warning("All AI providers exhausted. Waiting 5 minutes...")
                time.sleep(300)
                self.reset_providers()
                continue

            stdout, rc = self._invoke(provider_name, prompt, tier, timeout,
                                      allow_edits, cwd)

            if rc == 0:
                return stdout, rc, provider_name

            log.warning(f"AI: {provider_name} failed (rc={rc})")
            if not provider_override:
                self.disable_provider(provider_name)
            else:
                log.warning(f"Override provider {provider_name} failed. Waiting...")
                time.sleep(300)

    def _invoke(self, provider_name, prompt, tier, timeout, allow_edits, cwd):
        spec = PROVIDERS[provider_name]
        model = spec["models"][tier]

        if allow_edits:
            cmd = spec["cmd_edit"](model)
        else:
            cmd = spec["cmd_text"](model)

        env = os.environ.copy()
        for var in spec["env_cleanup"]:
            env.pop(var, None)

        log.info(f"AI: calling {provider_name}/{model} (edits={allow_edits})")

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
