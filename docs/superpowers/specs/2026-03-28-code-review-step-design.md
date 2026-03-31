# Code Review Step — Design Spec

## Problem

The optimiser's LLM-generated code changes sometimes introduce maintainability issues that pass build and quality checks but get flagged in human review:

- **Stale comments** left behind after refactoring (commit 3a28481)
- **Large macros** instead of structured specialization helpers (commit 662ff7c, DIFFUSE_ROW_LOOP)
- **Duplicated code** from unswitching without factoring into helper functions (commit bede39b, DIFFUSE_PIXEL_BODY)
- **Specialization-boundary regressions** where a refactor keeps the code readable but collapses many specialized outer paths into one generic parallel helper
- **OpenCL contamination** — modifications to `_cl` functions that aren't tested by the CPU benchmark path

These are cheap to detect with a focused checklist review, but expensive to fix after commit.

## Solution

Add a **CODE_REVIEW** step between CODE (LLM edits files) and BUILD (compile + test). A cheaper LLM tier reviews the diff against a narrow, project-specific checklist.

### Flow

```
CODE → CODE_REVIEW → BUILD → TEST → BENCHMARK
 ↑          |
 └──────────┘ (feedback → retry)
```

1. After CODE produces edits, get the `git diff` of changed files within `commit_scope`.
2. Send diff + checklist to cheaper LLM (tier="normal" — Sonnet/Flash).
3. Parse response:
   - **LGTM** (first line) → proceed to BUILD.
   - **Anything else** → treat as review feedback, save to `errors.txt`, loop back to CODE.
4. If review LLM call fails (rc != 0) → log warning, skip review, proceed to BUILD.
5. Review rejections decrement `retries_left` (same budget as build/quality failures).

### Checklist

The review prompt instructs the LLM to check ONLY these items:

1. **Stale comments**: Are there comments that no longer describe the code they annotate?
2. **Macro misuse**: Were giant body macros introduced? Avoid those, but do not approve a refactor just because it uses inline functions.
3. **Unswitched duplication**: Is there duplicated code from loop unswitching that should be factored into `always_inline` helper functions?
4. **Specialization-boundary regressions**: Did specialized outer dispatch get collapsed into a single helper that now contains `DT_OMP_FOR()` or the parallel row loop while taking hot-path flags as ordinary parameters? Did many unswitched entry paths get merged into one runtime-branching loop?
5. **OpenCL contamination**: Were any `_cl` functions or OpenCL-only code paths modified without necessity?

The checklist is derived from `instructions.md` content and hardcoded in the prompt. Future iterations may make it configurable.

### LLM Configuration

- **Tier**: "normal" (maps to Sonnet for Claude, Flash for Gemini)
- **Allow edits**: No (text-only response)
- **Timeout**: Uses `llm_timeout` from settings
- **Purpose**: "reviewing code changes"

### Response Protocol

The review LLM must respond with exactly `LGTM` on the first line if all checks pass. Any other first line means the review found issues — the entire response is treated as feedback.

### Retry Behaviour

- Review feedback writes to `ideas/coding/errors.txt` (same path used by build failures)
- The implementation LLM sees the feedback as "PREVIOUS ATTEMPT FAILED" context
- Each review rejection decrements `retries_left`
- When retries exhaust, idea fails with outcome "code review failure"

## Components Changed

| File | Change |
|------|--------|
| `optimise/git.py` | Add `diff_scope(scope)` method — returns unified diff of changes within scope prefixes |
| `optimise/prompts.py` | Add `build_code_review_prompt(instructions, diff, idea_content)` |
| `optimise/runner.py` | Add `parse_code_review_response(text)` — returns `(approved: bool, feedback: str)` |
| `optimise/cli.py` | Add `_do_code_review()` function, wire between CODE success and BUILD |

## Not In Scope

- Configurable checklist items (future)
- Review of non-diff context (e.g., surrounding code)
- Review step as a separate state in `StartupState` (it's inline within CODE)
