# Code Review Step — Implementation Plan

**Spec**: `docs/superpowers/specs/2026-03-28-code-review-step-design.md`

All steps follow red/green TDD: write failing test first, then implement.

## Step 1: GitRepo.diff_scope()

### 1a. Tests (`tests/test_git.py`)

Add `TestDiffScope` class:

- `test_returns_diff_for_changed_files_in_scope`: Modify `src/main.c`, call `diff_scope(["src/"])`, assert diff contains the change.
- `test_excludes_changes_outside_scope`: Modify both `src/main.c` and `tests/test.c`, call `diff_scope(["src/"])`, assert only `src/main.c` appears in diff.
- `test_returns_empty_string_when_no_changes`: Clean repo, call `diff_scope(["src/"])`, assert returns `""`.
- `test_none_scope_returns_all_changes`: Modify files, call `diff_scope(None)`, assert all changes appear.

### 1b. Implementation (`optimise/git.py`)

Add `diff_scope(self, scope=None)` method to `GitRepo`:
- Run `git diff HEAD -- <scope_prefixes>` (or `git diff HEAD` if no scope)
- Return stdout as string

## Step 2: build_code_review_prompt()

### 2a. Tests (`tests/test_prompts.py`)

Add `TestCodeReviewPrompt` class:

- `test_includes_diff`: Assert the diff text appears in the prompt.
- `test_includes_instructions`: Assert instructions text appears.
- `test_includes_idea_content`: Assert idea content appears.
- `test_includes_checklist_items`: Assert all 4 checklist items appear (stale comments, macros, duplication, OpenCL).
- `test_specifies_lgtm_response_format`: Assert "LGTM" appears as the expected approval response.
- `test_prohibits_edits`: Assert prompt tells reviewer not to make edits.

### 2b. Implementation (`optimise/prompts.py`)

Add `build_code_review_prompt(instructions, diff, idea_content)` function.

## Step 3: parse_code_review_response()

### 3a. Tests (`tests/test_runner.py`)

Add `TestParseCodeReviewResponse` class:

- `test_lgtm_returns_approved`: Input `"LGTM"` → `(True, "")`.
- `test_lgtm_with_trailing_newline`: Input `"LGTM\n"` → `(True, "")`.
- `test_feedback_returns_not_approved`: Input `"Issue: stale comment on line 42"` → `(False, "Issue: stale comment on line 42")`.
- `test_empty_string_returns_not_approved`: Input `""` → `(False, "")`.
- `test_lgtm_case_insensitive`: Input `"lgtm"` → `(True, "")`.

### 3b. Implementation (`optimise/runner.py`)

Add `parse_code_review_response(text)` function:
- Strip text, check if first line (case-insensitive) is "LGTM"
- Return `(True, "")` if approved, `(False, full_text)` otherwise

## Step 4: Wire into cli.py

### 4a. Tests (`tests/test_cli.py`)

Add `TestDoCodeReview` class:

- `test_lgtm_returns_true`: Mock `ai.call` returning `"LGTM"`, mock `target_git.diff_scope` returning a diff. Assert `_do_code_review()` returns `(True, "")`.
- `test_feedback_returns_false_with_feedback`: Mock `ai.call` returning feedback text. Assert returns `(False, feedback_text)`.
- `test_llm_failure_returns_true`: Mock `ai.call` returning `("", 1, "provider")`. Assert returns `(True, "")` (skip review on failure).
- `test_empty_diff_skips_review`: Mock `target_git.diff_scope` returning `""`. Assert returns `(True, "")` without calling ai.
- `test_uses_normal_tier`: Assert `ai.call` is called with `tier="normal"`.
- `test_passes_llm_timeout`: Assert `ai.call` receives `timeout` from settings.

### 4b. Implementation (`optimise/cli.py`)

Add `_do_code_review(target_git, ai, settings, instructions, idea_content)`:
- Get diff via `target_git.diff_scope(settings.get("commit_scope"))`
- If empty diff, return `(True, "")`
- Build prompt via `build_code_review_prompt()`
- Call `ai.call(prompt, tier="normal", ...)`
- If rc != 0, log warning, return `(True, "")`
- Parse response via `parse_code_review_response()`
- Return result

### 4c. Integration in CODE block

In the CODE state, after successful LLM implementation and before `_do_build_test_benchmark()`:
1. Call `_do_code_review()`
2. If approved → proceed to build (existing flow)
3. If rejected → save feedback to `errors.txt`, decrement `retries_left`, set `state = CODE`, continue
4. Add import for `build_code_review_prompt` and `parse_code_review_response`

## Step 5: Update docs

- Update `CLAUDE.md` state machine diagram to show CODE_REVIEW
- Update `README.md` methodology section
- Update `docs/superpowers/specs/2026-03-14-optimiser-design.md` if it describes the state machine
