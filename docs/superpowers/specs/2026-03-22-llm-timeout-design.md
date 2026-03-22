# Design: Configurable LLM Timeout

## Summary

Make the LLM call timeout configurable via `llm_timeout` in `settings.conf`. Currently hardcoded as a 600-second default parameter in `AIRouter.call()`.

## Motivation

Different workloads and models have different response times. Users should be able to tune the timeout without editing source code.

## Design

### Settings layer (`settings.py`)

- Add `llm_timeout` to the optional integer settings with default `600`.
- Add `llm_timeout: 600` to `SETTINGS_TEMPLATE` under the "AI Providers" section with a comment explaining the setting.
- Validation: parsed as integer alongside `max_retries`, `max_iterations`, etc.

### CLI layer (`cli.py`)

- Pass `timeout=settings["llm_timeout"]` explicitly to all three `ai.call()` invocations:
  1. Idea generation
  2. Code implementation
  3. Learning review

### AI layer (`ai.py`)

- No changes. `call()` already accepts `timeout` as a parameter with default `600`. The default remains as a safety net but `cli.py` will always pass it explicitly.

### Settings template

Add to the "AI Providers" section of `SETTINGS_TEMPLATE`:

```
# Maximum time (seconds) to wait for an LLM response before timing out.
llm_timeout: 600
```

### Documentation

- `README.md`: Add `llm_timeout` to the settings reference.
- `docs/superpowers/specs/`: This file.

## Testing (red/green TDD)

1. **RED**: Test `llm_timeout` is parsed as integer from settings, defaults to `600` when omitted.
2. **GREEN**: Add to integer validation list with default.
3. **RED**: Test `llm_timeout` appears in `SETTINGS_TEMPLATE`.
4. **GREEN**: Add to template.
5. **RED**: Test each `ai.call()` site receives `timeout=settings["llm_timeout"]`.
6. **GREEN**: Wire through in `cli.py`.

## Non-goals

- Per-call-type timeouts (idea vs implementation vs learning) — can refine later.
- Timeout for build/benchmark/quality commands — intentionally unlimited.
