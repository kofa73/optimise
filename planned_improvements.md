# Planned Improvements

## Summary of Discussion

We investigated the optimiser hang and found two separate concerns:

1. Gemini quota exhaustion.
   - Live Gemini probes showed messages like:
     - `You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 5659ms...`
   - Some observed hangs were therefore at least partly caused by Gemini-side retry behavior, not only by the Python wrapper.

2. Router retry policy.
   - The current router behavior of waiting 2 hours and retrying forever after all providers fail was confirmed to be intentional.
   - A fail-fast change was proposed prematurely and was not aligned with that intended behavior.
   - We discussed making the exhausted-provider behavior configurable instead of hard-coded.

3. Configuration design.
   - We considered a simple `providers_retry_limit` setting.
   - We rejected negative sentinel values like `-1 means forever` as too inconsistent and awkward.
   - We then refined the idea toward bounded retries plus configurable exponential backoff.

4. Chosen direction.
   - Add explicit retry/backoff settings for exhausted providers.
   - Use exponential backoff starting at 5 minutes, doubling each time, capped at 160 minutes.
   - Also add a retry-count limit.
   - Implement via red/green TDD.

## Planned Retry / Backoff Design

### New settings

Add these settings to `settings.conf` handling:

- `providers_retry_limit`
  - non-negative integer
  - `0` means do not retry after a full exhausted-provider cycle
  - positive values mean retry that many exhausted cycles

- `providers_retry_initial_delay_seconds`
  - default: `300`

- `providers_retry_backoff_factor`
  - default: `2`

- `providers_retry_max_delay_seconds`
  - default: `9600`

### Backoff policy

When a single `AIRouter.call()` has tried all enabled providers and all have failed:

- if `providers_retry_limit == 0`, return failure immediately
- otherwise:
  - sleep for the current backoff delay
  - reset providers
  - retry another exhausted cycle
  - increase the delay by multiplying by `providers_retry_backoff_factor`
  - clamp the delay to `providers_retry_max_delay_seconds`

With defaults, the delays are:

- 300s
- 600s
- 1200s
- 2400s
- 4800s
- 9600s
- 9600s thereafter

### Important policy choices

- No negative sentinel values.
- `provider_override` should remain bounded:
  - if the override provider fails, return failure immediately
  - do not enter exhausted-provider retry loops for override calls
- Keep the existing short per-provider cooldown logic unchanged.

## TDD Plan

### Red

Add failing tests first for:

- settings parsing/defaults/validation of:
  - `providers_retry_limit`
  - `providers_retry_initial_delay_seconds`
  - `providers_retry_backoff_factor`
  - `providers_retry_max_delay_seconds`
- router behavior:
  - `providers_retry_limit=0` fails after one exhausted cycle
  - positive retry limit retries the correct number of full cycles
  - success after one exhausted cycle returns successfully
  - sleep delays follow exponential backoff and cap correctly
  - `provider_override` failure does not enter retry sleep
  - providers are reset between exhausted cycles

### Green

Implement the minimum production changes to satisfy the tests:

- `optimise/settings.py`
- `optimise/ai.py`
- `optimise/cli.py` to pass settings into `AIRouter`

## Changes Already Made During Investigation

### Non-mutating investigation

These exploration steps were completed:

- checked repo state in `/workspace/optimiser`
- read `optimise/ai.py`
- read `tests/test_ai.py`
- checked `gemini --help`
- ran limited Gemini probes and then stopped hammering Gemini after quota exhaustion became clear
- inspected settings, README references, and tests to understand how retry policy should fit the existing config model

### Findings from Gemini CLI inspection

`gemini --help` showed:

- non-interactive mode still uses `-p/--prompt`
- `--approval-mode` still exists with choices including:
  - `default`
  - `auto_edit`
  - `yolo`
  - `plan`

So the installed CLI still accepts the approval-mode flag shape currently referenced in the backend.

### Findings from code inspection

We found that current repo state already contains Gemini/retry-related edits:

- `optimise/ai.py`
  - Gemini text command was changed to add `--approval-mode=plan`
  - Gemini `built_with` was bumped from `0.34.0` to `0.35.3`
  - Claude `built_with` was bumped from `2.1.81` to `2.1.87`
  - Claude text command gained `--permission-mode plan`
  - retry behavior was partially changed from:
    - wait 2 hours and retry forever
    - to fail fast after all providers fail
- `tests/test_ai.py`
  - tests were partially rewritten to expect fail-fast behavior instead of the intended infinite retry loop

These retry-related edits were identified as unapproved partial changes and should be cleaned up before implementing the new bounded exponential-backoff design.

## Specific Retry / Gemini Changes Currently Present In The Worktree

From the current diff:

### `optimise/ai.py`

- Added to Claude text command:
  - `--permission-mode plan`
- Changed Claude `built_with`:
  - `2.1.81` -> `2.1.87`
- Added to Gemini text command:
  - `--approval-mode=plan`
- Changed Gemini `built_with`:
  - `0.34.0` -> `0.35.3`
- Changed router call docstring from:
  - “Retries indefinitely with wait on full exhaustion.”
  - to fail-fast wording
- Changed exhausted-provider behavior from:
  - wait 2 hours, reset providers, continue forever
  - to immediate failure return
- Changed `provider_override` failure handling from:
  - wait and continue
  - to immediate return

### `tests/test_ai.py`

- Reworked retry-related tests away from infinite-retry assumptions
- Added a fail-fast style override test
- Existing modified tests currently reflect the aborted fail-fast attempt, not the agreed backoff design

### Test runs performed

- `python3 -m pytest tests/test_prompts.py -q`
  - passed: `14 passed`
- `python3 -m pytest tests/test_ai.py -q -k 'not GeminiIntegration and not ClaudeIntegration'`
  - failed after the partial fail-fast edits because two tests still expected a provider name instead of the new `None` return on exhausted providers
- `python3 -m pytest tests -q -k 'not GeminiIntegration and not ClaudeIntegration'`
  - showed the same failure pattern before the run was interrupted

## Scope Decision

The agreed implementation scope is:

- do implement configurable exhausted-provider retry count plus exponential backoff
- do not bundle a broader Gemini command-contract rewrite into the same patch
- Gemini CLI invocation can be revisited separately if needed, but it is not part of this planned change

## Implementation Notes

Before implementing the new TDD plan:

1. Revert only the unapproved retry-policy test/code changes in:
   - `optimise/ai.py`
   - `tests/test_ai.py`
2. Keep unrelated Gemini and Claude version/flag changes under separate scrutiny instead of mixing them into the retry-policy patch.
3. Then implement the new settings and exponential backoff behavior from a clean baseline.

## Recommended Defaults

- `providers_retry_limit: 0`
- `providers_retry_initial_delay_seconds: 300`
- `providers_retry_backoff_factor: 2`
- `providers_retry_max_delay_seconds: 9600`
