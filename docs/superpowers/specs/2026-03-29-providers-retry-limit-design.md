# providers_retry_limit — Phase 1 Design

## Problem

When all AI providers fail (e.g. Gemini quota exhaustion), the router retries
indefinitely with a 2-hour wait between cycles. This causes tests to hang when
the only enabled provider is unavailable.

## Goal

Add a `providers_retry_limit` setting so the router fails after a bounded
number of exhausted-provider cycles. Default 0 (fail immediately) makes tests
safe. Production configs set a high value for unattended runs.

## Scope

Phase 1 only. Configurable exponential backoff (initial delay, factor, max
delay) is deferred to phase 2.

## Changes

### `optimise/settings.py`

- Add `providers_retry_limit` to `_INT_KEYS`.
- In `validate_settings()`: default to `0` if not present.
- In `SETTINGS_TEMPLATE`: add under "AI Providers" section with value `1000`
  and a comment explaining it controls how many times the router retries after
  all providers fail, with a 2-hour wait between cycles.

### `optimise/ai.py`

**Remove `provider_override`:** The parameter on `call()` is dead code — no
caller in the codebase passes it. Integration tests already use single-provider
constructors (`AIRouter(providers=["gemini"])`). Remove the parameter, the
branch in `call()` that checks it, and the 300s sleep on override failure.

**Add `providers_retry_limit` to `AIRouter.__init__`:**

```python
def __init__(self, providers=None, disabled_providers=None,
             providers_retry_limit=0):
```

Store as `self.providers_retry_limit`.

**Modify `call()` exhaustion logic:**

Current committed code:

```python
if provider_name is None:
    log.warning("All AI providers exhausted. Waiting 2 hours...")
    time.sleep(7200)
    self.reset_providers()
    continue
```

New code:

```python
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
```

`retries_used` is a local variable in `call()`, initialized to `0`.

### `optimise/cli.py`

Pass the setting through to the router constructor:

```python
AIRouter(
    disabled_providers=settings.get("disabled_providers", []),
    providers_retry_limit=settings.get("providers_retry_limit", 0),
)
```

### Revert from worktree

- Gemini `built_with`: `0.35.3` → `0.34.0`
- Gemini `cmd_text`: remove `--approval-mode=plan`
- The ad-hoc fail-fast changes in `call()` (replaced by the new parameterized logic)
- The `provider_override` immediate-return behavior (parameter removed entirely)
- Tests rewritten to expect fail-fast (replaced by new retry-limit tests)

### Keep from worktree

- Claude `built_with`: `2.1.87` (address separately)
- Claude `--permission-mode plan` (address separately)

## Test Plan (TDD — red first)

### Settings tests

1. `providers_retry_limit` parsed as int from config.
2. `providers_retry_limit` defaults to `0` when absent.
3. `SETTINGS_TEMPLATE` contains `providers_retry_limit`.

### Router tests

4. `providers_retry_limit=0`: all providers fail → returns `("", 1, None)`
   after one cycle, no `time.sleep(7200)` called.
5. `providers_retry_limit=2`: all providers fail every cycle → returns failure
   after 3 total cycles (initial + 2 retries), `time.sleep(7200)` called twice.
6. `providers_retry_limit=1`: first cycle all fail, second cycle succeeds →
   returns success, `time.sleep(7200)` called once.

### Removed tests

7. Remove `test_call_with_override_returns_failure_without_waiting` (parameter gone).
8. Update rate-limiting tests that used `provider_override` to use
   single-provider constructors instead.

## Not in scope

- Configurable backoff delay/factor/max (phase 2).
- Gemini version/flag update (separate follow-up).
- Claude version/flag changes (separate follow-up).
