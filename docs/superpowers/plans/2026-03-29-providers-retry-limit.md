# providers_retry_limit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `providers_retry_limit` setting so the AI router fails after a bounded number of exhausted-provider cycles instead of retrying indefinitely.

**Architecture:** New integer setting parsed in `settings.py`, passed to `AIRouter.__init__`, governs the exhaustion branch in `call()`. Default 0 (fail immediately). Also removes the dead `provider_override` parameter.

**Tech Stack:** Python 3.10+, pytest, unittest.mock

---

### Task 1: Revert worktree changes to ai.py and test_ai.py

Start from the committed (HEAD) versions so all subsequent changes are clean.

**Files:**
- Restore: `optimise/ai.py`
- Restore: `tests/test_ai.py`

- [ ] **Step 1: Restore committed versions**

```bash
git checkout HEAD -- optimise/ai.py tests/test_ai.py
```

- [ ] **Step 2: Verify tests pass on clean baseline**

Run: `python3 -m pytest tests/test_ai.py -v -k 'not GeminiIntegration and not ClaudeIntegration'`
Expected: All tests PASS (the committed code with infinite retry is the baseline)

- [ ] **Step 3: Commit the revert**

```bash
git add optimise/ai.py tests/test_ai.py
git commit -m "revert: restore committed ai.py and test_ai.py before retry-limit work"
```

---

### Task 2: Write failing settings tests

**Files:**
- Test: `tests/test_settings.py`

- [ ] **Step 1: Add three failing tests to TestValidateSettings**

Append these tests to the `TestValidateSettings` class at the end of `tests/test_settings.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_settings.py -v -k providers_retry_limit`
Expected: 3 FAILED — `providers_retry_limit` not yet in `_INT_KEYS`, no default, not in template

---

### Task 3: Make settings tests pass

**Files:**
- Modify: `optimise/settings.py:21-25` (`_INT_KEYS`)
- Modify: `optimise/settings.py:159-162` (defaults section, after `llm_timeout`)
- Modify: `optimise/settings.py:254-260` (`SETTINGS_TEMPLATE` AI Providers section)

- [ ] **Step 1: Add to `_INT_KEYS`**

In `optimise/settings.py`, add `"providers_retry_limit"` to the `_INT_KEYS` list:

```python
_INT_KEYS = [
    "num_warmup_iterations", "benchmark_convergence_tail_runs",
    "max_retries", "max_iterations", "max_consecutive_perf_failures",
    "max_runtime_minutes", "idea_generation_batch_size", "llm_timeout",
    "providers_retry_limit",
]
```

- [ ] **Step 2: Add default in `validate_settings()`**

After the `llm_timeout` default block (line 161), add:

```python
    # Default providers_retry_limit
    if "providers_retry_limit" not in result:
        result["providers_retry_limit"] = 0
```

- [ ] **Step 3: Add to `SETTINGS_TEMPLATE`**

In the `SETTINGS_TEMPLATE` string, after the `llm_timeout: 3600` line and before the closing `"""`, add:

```
# How many times to retry after all providers fail in a single call.
# Each retry waits 2 hours for provider quota to reset.
# 0 = fail immediately (useful for testing). Set high for unattended runs.
providers_retry_limit: 1000
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_settings.py -v -k providers_retry_limit`
Expected: 3 PASSED

- [ ] **Step 5: Run full settings test suite**

Run: `python3 -m pytest tests/test_settings.py -v`
Expected: All PASSED (no regressions)

- [ ] **Step 6: Commit**

```bash
git add optimise/settings.py tests/test_settings.py
git commit -m "feat: add providers_retry_limit setting (default 0)"
```

---

### Task 4: Write failing router retry tests

**Files:**
- Test: `tests/test_ai.py`

- [ ] **Step 1: Add new `TestProvidersRetryLimit` class**

Add this class after `TestAIRouter` in `tests/test_ai.py`:

```python
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
            stdout, rc, provider = router.call("test", allow_edits=False)
        assert stdout == ""
        assert rc == 1
        assert provider is None
        mock_sleep.assert_not_called()

    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_retry_limit_two_retries_then_fails(self, mock_run, mock_which):
        """retry_limit=2: 3 total cycles (initial + 2 retries), all fail."""
        router = AIRouter(providers=["claude"], providers_retry_limit=2)
        mock_run.return_value = MagicMock(stdout="", returncode=1)
        with patch("time.sleep") as mock_sleep:
            stdout, rc, provider = router.call("test", allow_edits=False)
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
            stdout, rc, provider = router.call("test", allow_edits=False)
        assert stdout == "ok"
        assert rc == 0
        assert provider == "claude"
        sleep_calls = [c for c in mock_sleep.call_args_list if c[0][0] == 7200]
        assert len(sleep_calls) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_ai.py::TestProvidersRetryLimit -v`
Expected: 3 FAILED — `AIRouter.__init__` does not accept `providers_retry_limit` yet

---

### Task 5: Implement router retry logic

**Files:**
- Modify: `optimise/ai.py:70` (`__init__` signature)
- Modify: `optimise/ai.py:124-166` (`call()` method)

- [ ] **Step 1: Add `providers_retry_limit` to `__init__`**

Change the `__init__` signature and store the value:

```python
    def __init__(self, providers=None, disabled_providers=None,
                 providers_retry_limit=0):
```

At the end of `__init__`, after `self._last_call_finish_time = ...` (line 96), add:

```python
        self.providers_retry_limit = providers_retry_limit
```

- [ ] **Step 2: Replace the exhaustion branch in `call()`**

Replace the entire `call()` method with:

```python
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
```

This removes `provider_override` entirely and replaces the infinite-retry exhaustion branch with bounded retry.

- [ ] **Step 3: Run new retry tests**

Run: `python3 -m pytest tests/test_ai.py::TestProvidersRetryLimit -v`
Expected: 3 PASSED

---

### Task 6: Fix existing tests broken by provider_override removal

The committed tests use `provider_override` in several places. Now that the parameter is gone, update them.

**Files:**
- Modify: `tests/test_ai.py`

- [ ] **Step 1: Fix `test_call_disables_on_failure`**

The committed test expects success after infinite retry. With `providers_retry_limit=0` (default), it should expect failure after one exhausted cycle. Replace the test (in class `TestAIRouter`):

```python
    @patch("shutil.which", return_value="/usr/bin/fake")
    @patch("subprocess.run")
    def test_call_disables_on_failure(self, mock_run, mock_which):
        router = AIRouter(providers=["claude", "gemini"])
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="", returncode=1),
        ]
        stdout, rc, provider = router.call("test", allow_edits=False)
        assert stdout == ""
        assert rc == 1
        assert provider is None
        assert mock_run.call_count == 2
```

- [ ] **Step 2: Fix `test_version_warning_repeated_on_failure`**

The test captures version warnings during failures. With `providers_retry_limit=0`, the call returns after exhausting both providers. The version warning is still logged. Replace (in class `TestVersionWarnings`):

```python
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
            router.call("test", allow_edits=False)
        assert any("consider updating the script" in r.message for r in caplog.records)
```

- [ ] **Step 3: Fix rate-limiting tests that used `provider_override`**

In class `TestRateLimiting`, four tests pass `provider_override="claude"`. Remove that kwarg from each. The tests already construct with `providers=["claude"]`, so the single provider is always selected. Change these four tests:

`test_delay_when_last_call_recent` (line 294): remove `provider_override="claude"` from the `router.call(...)` line.

`test_no_delay_when_last_call_old` (line 308): remove `provider_override="claude"` from the `router.call(...)` line.

`test_last_call_finish_time_updated_after_call` (line 317): remove `provider_override="claude"` from the `router.call(...)` line.

`test_delay_logs_message` (line 332): remove `provider_override="claude"` from the `router.call(...)` line.

- [ ] **Step 4: Run full test suite**

Run: `python3 -m pytest tests/test_ai.py -v -k 'not GeminiIntegration and not ClaudeIntegration'`
Expected: All PASSED

- [ ] **Step 5: Commit**

```bash
git add optimise/ai.py tests/test_ai.py
git commit -m "feat: add providers_retry_limit to AIRouter, remove dead provider_override"
```

---

### Task 7: Wire up cli.py and run full suite

**Files:**
- Modify: `optimise/cli.py:186`

- [ ] **Step 1: Pass providers_retry_limit to AIRouter**

Change line 186 in `optimise/cli.py` from:

```python
    ai = AIRouter(disabled_providers=settings.get("disabled_providers", []))
```

to:

```python
    ai = AIRouter(
        disabled_providers=settings.get("disabled_providers", []),
        providers_retry_limit=settings.get("providers_retry_limit", 0),
    )
```

- [ ] **Step 2: Run full test suite**

Run: `python3 -m pytest tests/ -v -k 'not GeminiIntegration and not ClaudeIntegration'`
Expected: All PASSED

- [ ] **Step 3: Commit**

```bash
git add optimise/cli.py
git commit -m "wire: pass providers_retry_limit from settings to AIRouter"
```

---

### Task 8: Update documentation

**Files:**
- Modify: `docs/superpowers/specs/2026-03-29-providers-retry-limit-design.md` (mark complete)

- [ ] **Step 1: Verify no doc updates needed in CLAUDE.md**

The `CLAUDE.md` architecture section does not mention retry behavior, so no changes are needed there. Check that `README.md` doesn't reference provider_override either (it shouldn't — grep to confirm).

```bash
grep -n provider_override README.md CLAUDE.md
```

Expected: no matches (or only in docs/superpowers/ files which are internal)

- [ ] **Step 2: Final full test run**

Run: `python3 -m pytest tests/ -v -k 'not GeminiIntegration and not ClaudeIntegration'`
Expected: All PASSED
