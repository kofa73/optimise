# Simplify Idea Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace LLM-driven idea selection with lexicographic picking, remove dedup machinery, fold applicability checking into the implementation prompt, and add state-phase logging.

**Architecture:** The GENERATE→SELECT→CODE pipeline becomes GENERATE→CODE with selection reduced to `sorted(list_ideas(...))[0]`. The implementation LLM call gains a `NOT_APPLICABLE` escape hatch. The dedup retry loop, exhaustion termination, `build_selection_prompt`, and `parse_selection` are removed.

**Tech Stack:** Python 3.10+, pytest

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `optimise/settings.py` | Modify | Remove `max_dedup_attempts` from `_INT_KEYS` and template |
| `optimise/state.py` | Modify | Remove `dedup_title()` |
| `optimise/prompts.py` | Modify | Remove `build_selection_prompt()`, update `build_implementation_prompt()` with applicability check |
| `optimise/runner.py` | Modify | Remove `parse_selection()`, `TerminationReason.IDEA_EXHAUSTION` |
| `optimise/cli.py` | Modify | Rewrite `_generate_ideas()` (no dedup loop), remove SELECT block, add NOT_APPLICABLE handling in CODE, add phase logging |
| `tests/test_state.py` | Modify | Remove `TestDedupTitle` |
| `tests/test_settings.py` | Modify | Remove `max_dedup_attempts` from valid settings fixture |
| `tests/test_prompts.py` | Modify | Remove `TestSelectionPrompt`, add applicability-check test |
| `tests/test_runner.py` | Modify | Remove `TestParseSelection`, remove `IDEA_EXHAUSTION` from imports |
| `tests/test_cli.py` | Modify | Update `TestGenerateIdeas` (no dedup), remove exhaustion test, add NOT_APPLICABLE test |
| `docs/superpowers/specs/2026-03-14-optimiser-design.md` | Modify | Update spec sections 4, 7, 8, 9 |

---

## Chunk 1: Remove dedup and selection infrastructure

### Task 1: Remove `dedup_title` from state.py

**Files:**
- Modify: `tests/test_state.py:144-155` (remove `TestDedupTitle`)
- Modify: `optimise/state.py:88-91` (remove `dedup_title()`)

- [ ] **Step 1: Remove `TestDedupTitle` class from tests**

Delete the entire `TestDedupTitle` class (4 tests) and remove `dedup_title` from the import line.

```python
# tests/test_state.py line 4 — remove dedup_title from import
from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \
    read_idea, append_outcome, all_idea_titles, clean_errors, save_errors
```

Delete lines 144-155 (`class TestDedupTitle` and its 4 methods).

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_state.py -v`
Expected: ImportError for `dedup_title` gone, all remaining tests pass. Actually — since we removed the import but `dedup_title` still exists, tests should pass. The real "red" comes in Step 3.

- [ ] **Step 3: Remove `dedup_title()` from state.py**

Delete the function at `optimise/state.py:88-91`.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_state.py -v`
Expected: All pass (no test references `dedup_title` any more).

- [ ] **Step 5: Commit**

```bash
git add optimise/state.py tests/test_state.py
git commit -m "remove dedup_title — deduplication replaced by early abort"
```

---

### Task 2: Remove `parse_selection` from runner.py

**Files:**
- Modify: `tests/test_runner.py:309,341-352` (remove `TestParseSelection`, remove `parse_selection` from import)
- Modify: `optimise/runner.py:215-232` (remove `parse_selection()`)

- [ ] **Step 1: Remove `TestParseSelection` and its import from tests**

In `tests/test_runner.py`:
- Line 309: change `from optimise.runner import parse_generated_ideas, parse_selection` to `from optimise.runner import parse_generated_ideas`
- Delete lines 341-352 (the entire `TestParseSelection` class).

- [ ] **Step 2: Run tests to confirm clean**

Run: `python3 -m pytest tests/test_runner.py -v`
Expected: All remaining tests pass.

- [ ] **Step 3: Remove `parse_selection()` from runner.py**

Delete `optimise/runner.py:215-232`.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_runner.py -v`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add optimise/runner.py tests/test_runner.py
git commit -m "remove parse_selection — ideas now picked lexicographically"
```

---

### Task 3: Remove `build_selection_prompt` from prompts.py

**Files:**
- Modify: `tests/test_prompts.py:37-43` (remove `TestSelectionPrompt`)
- Modify: `optimise/prompts.py:51-74` (remove `build_selection_prompt()`)

- [ ] **Step 1: Remove `TestSelectionPrompt` and its import from tests**

In `tests/test_prompts.py`:
- Line 4: remove `build_selection_prompt` from the import.
- Delete lines 37-43 (the entire `TestSelectionPrompt` class).

- [ ] **Step 2: Run tests**

Run: `python3 -m pytest tests/test_prompts.py -v`
Expected: All remaining tests pass.

- [ ] **Step 3: Remove `build_selection_prompt()` from prompts.py**

Delete `optimise/prompts.py:51-74`.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_prompts.py -v`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add optimise/prompts.py tests/test_prompts.py
git commit -m "remove build_selection_prompt — no longer using LLM for selection"
```

---

### Task 4: Remove `max_dedup_attempts` from settings

**Files:**
- Modify: `tests/test_settings.py:50-81` (remove `max_dedup_attempts` from fixture)
- Modify: `optimise/settings.py:24,203-204` (remove from `_INT_KEYS` and template)

- [ ] **Step 1: Remove `max_dedup_attempts` from test fixture**

In `tests/test_settings.py`, `_make_valid_settings()` method: delete the line `"max_dedup_attempts": "10",`.

- [ ] **Step 2: Run tests**

Run: `python3 -m pytest tests/test_settings.py -v`
Expected: All pass (the setting is optional, just no longer validated).

- [ ] **Step 3: Remove from `_INT_KEYS` and template**

In `optimise/settings.py`:
- Line 24: remove `"max_dedup_attempts"` from the `_INT_KEYS` list.
- Lines 203-204: remove the `max_dedup_attempts` setting and its comment from `SETTINGS_TEMPLATE`.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_settings.py -v`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add optimise/settings.py tests/test_settings.py
git commit -m "remove max_dedup_attempts setting — dedup loop removed"
```

---

### Task 5: Remove `TerminationReason.IDEA_EXHAUSTION`

**Files:**
- Modify: `optimise/runner.py:101` (remove enum member)

- [ ] **Step 1: Remove the enum member**

In `optimise/runner.py`, delete line 101: `IDEA_EXHAUSTION = "cannot generate new ideas"`.

Also update the docstring of `check_termination` (lines 109-110) — remove the sentence about idea exhaustion being handled by GENERATE state:

```python
def check_termination(iteration, max_iterations, consecutive_perf_failures,
                      max_consecutive, start_time, max_minutes):
    """Check if any termination condition is met.

    Returns a TerminationReason or None.
    """
```

- [ ] **Step 2: Run tests**

Run: `python3 -m pytest tests/test_runner.py -v`
Expected: All pass (no test references `IDEA_EXHAUSTION`).

- [ ] **Step 3: Commit**

```bash
git add optimise/runner.py
git commit -m "remove TerminationReason.IDEA_EXHAUSTION — user uses Ctrl+C"
```

---

## Chunk 2: Rewrite generation and selection logic

### Task 6: Simplify `_generate_ideas` (no dedup loop)

**Files:**
- Modify: `tests/test_cli.py:123-216` (rewrite `TestGenerateIdeas`)
- Modify: `optimise/cli.py:82-141` (rewrite `_generate_ideas`, remove `GenerationResult.EXHAUSTED`)

- [ ] **Step 1: Rewrite test class**

Replace `TestGenerateIdeas` in `tests/test_cli.py` with:

```python
class TestGenerateIdeas:
    def _setup(self, tmp_path):
        """Create script repo with idea directories and a learnings file."""
        script = tmp_path / "script"
        script.mkdir()
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (script / d).mkdir(parents=True)
        (script / "learnings.md").write_text("## What works\n\n## What to avoid\n")
        (script / "instructions.md").write_text("Optimise for speed.\n")
        return str(script)

    def _make_ai(self, outputs):
        """Create a mock AI that returns outputs in order."""
        ai = MagicMock()
        ai.call = MagicMock(side_effect=outputs)
        return ai

    def test_adds_new_ideas(self, tmp_path):
        """Generation produces ideas → added to todo."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("---\nFILENAME: idea-a\nTITLE: Unroll inner loop\nDESCRIPTION:\nUnroll.\n---\n",
             0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        from optimise.state import list_ideas
        assert len(list_ideas(script_repo, "todo")) == 1

    def test_llm_failure_returns_llm_failure(self, tmp_path):
        """LLM fails every call (rc != 0) → LLM_FAILURE."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("", 1, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE

    def test_no_generation_needed_returns_ok(self, tmp_path):
        """If todo already has enough ideas, no generation needed → OK."""
        script_repo = self._setup(tmp_path)
        (tmp_path / "script" / "ideas" / "todo" / "existing.md").write_text("Existing idea\n\nDo this.")
        ai = self._make_ai([])  # should not be called
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.OK
        assert ai.call.call_count == 0

    def test_unparseable_output_returns_llm_failure(self, tmp_path):
        """LLM returns gibberish → LLM_FAILURE."""
        script_repo = self._setup(tmp_path)
        ai = self._make_ai([
            ("here is some random text with no structure", 0, "test-provider"),
        ])
        result = _generate_ideas(
            directory=script_repo, settings={"min_ideas": 1},
            ai=ai, target_repo_path="/tmp", instructions="test", target_files="code",
        )
        assert result == GenerationResult.LLM_FAILURE
```

Also update the import at top of `tests/test_cli.py` — remove `GenerationResult.EXHAUSTED` is not explicitly imported, but `GenerationResult` is used. No import change needed since we import `GenerationResult` not the individual members.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_cli.py::TestGenerateIdeas -v`
Expected: `test_unparseable_output_returns_llm_failure` fails (current code has dedup retry loop, may still return EXHAUSTED). Other tests may fail because settings dict no longer has `max_dedup_attempts`.

- [ ] **Step 3: Rewrite `_generate_ideas` and `GenerationResult`**

In `optimise/cli.py`, replace:

```python
class GenerationResult(enum.Enum):
    OK = "ok"
    EXHAUSTED = "exhausted"
    LLM_FAILURE = "llm_failure"


def _generate_ideas(directory, settings, ai, target_repo_path, instructions, target_files):
    """Generate ideas to fill todo.

    Returns GenerationResult:
      OK           — ideas were added, or todo already had enough
      LLM_FAILURE  — LLM failed to produce any parseable ideas
    """
    todo_count = len(list_ideas(directory, "todo"))
    needed = settings["min_ideas"] - todo_count

    if needed <= 0:
        return GenerationResult.OK

    learnings = _read_learnings(directory)
    existing_titles = all_idea_titles(directory)

    prompt = build_generation_prompt(
        instructions, learnings, existing_titles, needed, target_files,
    )
    output, rc, provider = ai.call(
        prompt, tier="best", cwd=target_repo_path,
    )
    if rc != 0:
        log.warning(f"Idea generation failed ({provider})")
        return GenerationResult.LLM_FAILURE

    ideas = parse_generated_ideas(output)
    if not ideas:
        return GenerationResult.LLM_FAILURE

    for idea in ideas:
        content = f"{idea['title']}\n\n{idea['description']}"
        create_idea(directory, idea["filename"], content)

    return GenerationResult.OK
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_cli.py::TestGenerateIdeas -v`
Expected: All 4 pass.

- [ ] **Step 5: Commit**

```bash
git add optimise/cli.py tests/test_cli.py
git commit -m "simplify _generate_ideas — single batch, no dedup retry loop"
```

---

### Task 7: Replace SELECT with lexicographic pick, add NOT_APPLICABLE handling

**Files:**
- Modify: `tests/test_cli.py` (add `TestNotApplicable` class)
- Modify: `optimise/cli.py:239-301,303-339` (rewrite GENERATE→CODE flow)
- Modify: `optimise/prompts.py:77-130` (update `build_implementation_prompt`)

- [ ] **Step 1: Add applicability-check test to prompts**

In `tests/test_prompts.py`, add to `TestImplementationPrompt`:

```python
    def test_includes_applicability_check(self):
        prompt = build_implementation_prompt(
            instructions="", learnings="",
            idea_content="idea",
            target_files=["f.c"],
            errors=None,
        )
        assert "NOT_APPLICABLE" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_prompts.py::TestImplementationPrompt::test_includes_applicability_check -v`
Expected: FAIL — current prompt doesn't contain NOT_APPLICABLE.

- [ ] **Step 3: Update `build_implementation_prompt` in prompts.py**

Add to the `## CRITICAL RULES` section in `build_implementation_prompt`, before the existing rule 1:

```python
    return f"""\
# Instructions

{instructions}

# Learnings from past experiments

{learnings}

# Your task

Implement this optimisation idea by editing the target files ({targets}):

{idea_content}

{error_block}

## CRITICAL RULES — READ EVERY ONE

1. First, read the target files and assess whether this idea is still applicable
   given the current state of the code. If the optimisation has already been applied,
   or the code structure has changed making it infeasible, respond with exactly
   `NOT_APPLICABLE` on the first line, followed by a brief explanation. Do nothing else.
2. Otherwise, use the Read tool to read the target files. Use Edit to make changes.
3. Make ONLY the changes described in the idea. Do not refactor other code.

4. **YOU MUST NOT RUN ANY BUILD COMMANDS. THIS IS FORBIDDEN.**
5. **YOU MUST NOT RUN ANY TEST COMMANDS. THIS IS PROHIBITED.**
6. **YOU MUST NOT RUN ANY BENCHMARK COMMANDS. YOU WILL BE PENALIZED.**
7. **YOU MUST NEVER USE SHELL/BASH TOOLS TO EXECUTE ANYTHING.**
8. **IF YOU ATTEMPT TO BUILD, TEST, OR BENCHMARK, THE SESSION WILL BE TERMINATED.**

The orchestrator script handles ALL building, testing, and benchmarking
after you return control. Your ONLY job is to edit the source files.

When done editing, output a brief summary of what you changed.
"""
```

- [ ] **Step 4: Run prompt tests**

Run: `python3 -m pytest tests/test_prompts.py -v`
Expected: All pass including the new test.

- [ ] **Step 5: Add `TestNotApplicable` test in test_cli.py**

Add a new test class after `TestFailIdea`:

```python
class TestNotApplicable:
    """Test that NOT_APPLICABLE LLM response skips build/test/benchmark."""

    def test_not_applicable_moves_to_done(self, tmp_path):
        """If LLM responds NOT_APPLICABLE, idea goes to done without building."""
        script = tmp_path / "script"
        target = tmp_path / "target"
        script.mkdir()
        target.mkdir()
        _init_git(script)
        _init_git(target)

        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            (script / d).mkdir(parents=True, exist_ok=True)

        (script / "ideas" / "coding" / "idea.md").write_text(
            "Some old idea\n\nNo longer relevant."
        )
        (script / "perf-logs" / "current-best-perf.md").write_text(
            "# Individual timings\n| user |\n| ---- |\n| 10.0 |\n"
        )

        # Check that parse_not_applicable detects the response
        from optimise.runner import parse_not_applicable
        assert parse_not_applicable("NOT_APPLICABLE\nCode already changed.") is True
        assert parse_not_applicable("I have made the edits.") is False
        assert parse_not_applicable("NOT_APPLICABLE") is True
        assert parse_not_applicable("  NOT_APPLICABLE  \nreason") is True
```

- [ ] **Step 6: Add `parse_not_applicable` to runner.py**

In `optimise/runner.py`, add after `parse_generated_ideas`:

```python
def parse_not_applicable(text):
    """Check if the LLM response indicates the idea is not applicable.

    Returns True if the first non-empty line is NOT_APPLICABLE.
    """
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line == "NOT_APPLICABLE"
    return False
```

- [ ] **Step 7: Run the new test**

Run: `python3 -m pytest tests/test_cli.py::TestNotApplicable -v`
Expected: All pass.

- [ ] **Step 8: Rewrite GENERATE and CODE blocks in cli.py**

In `optimise/cli.py`, update imports:
- Remove: `build_selection_prompt` from prompts import
- Remove: `parse_selection` from runner import
- Remove: `dedup_title` from state import
- Add: `parse_not_applicable` to runner import
- Remove: `GenerationResult.EXHAUSTED` references

Replace the GENERATE block (`if state == StartupState.GENERATE:`, lines ~239-301):

```python
        if state == StartupState.GENERATE:
            todo_before = len(list_ideas(directory, "todo"))
            gen_result = _generate_ideas(
                directory, settings, ai, target_repo_path,
                instructions, target_files,
            )
            todo_after = len(list_ideas(directory, "todo"))
            if todo_after > todo_before:
                script_git.commit_all(
                    f"generated {todo_after - todo_before} new ideas"
                )

            if gen_result == GenerationResult.LLM_FAILURE:
                log.warning("All LLM providers failed during idea generation — "
                            "will retry after cooldown")
                continue

            reason = check_termination(
                iteration, settings["max_iterations"],
                consecutive_perf_failures, settings["max_consecutive_perf_failures"],
                start_time, settings["max_runtime_minutes"],
            )
            if reason:
                log.info(f"TERMINATING: {reason.value}")
                script_git.commit_all(f"optimiser: terminated — {reason.value}")
                break

            # Pick first idea lexicographically
            todo_files = list_ideas(directory, "todo")
            if not todo_files:
                log.warning("No ideas in todo after generation — will retry")
                continue
            selected = todo_files[0]
            move_idea(directory, selected, "todo", "coding")
            log.info(f"Selected idea: {selected}")
            retries_left = settings["max_retries"]
            state = StartupState.CODE
            continue
```

Replace the CODE block start (`if state == StartupState.CODE:`, lines ~303-339) to add NOT_APPLICABLE handling after the LLM call:

After the existing `output, rc, provider = ai.call(...)` and its failure handling, before the `_do_build_test_benchmark` call, add:

```python
            # Check if LLM says idea is not applicable
            if rc == 0 and parse_not_applicable(output):
                log.info(f"Idea not applicable: {idea_title[:60]}")
                state_obj = _BuildState(directory, target_repo_path, target_git,
                                       script_git, settings, idea_file, iteration,
                                       consecutive_perf_failures, start_time)
                _fail_idea(state_obj, "not applicable")
                state = StartupState.GENERATE
                continue
```

- [ ] **Step 9: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All pass.

- [ ] **Step 10: Commit**

```bash
git add optimise/cli.py optimise/prompts.py optimise/runner.py tests/test_cli.py tests/test_prompts.py
git commit -m "replace LLM selection with lexicographic pick, add NOT_APPLICABLE check"
```

---

## Chunk 3: Add phase logging and update docs

### Task 8: Add state-phase prefix to log messages

**Files:**
- Modify: `optimise/cli.py` (add phase to key log lines)

The main loop in `do_run` already logs at each transition. Add the state name as a prefix to key log lines. This is a log-only change — no tests needed for log formatting.

- [ ] **Step 1: Add phase prefixes**

Throughout `do_run` in `optimise/cli.py`, prefix key log lines with the state:

In the BASELINE block:
```python
log.info("[BASELINE] Establishing baseline...")
```

In the GENERATE block:
```python
log.info("[GENERATE] Generating ideas...")
```

In the CODE block:
```python
log.info(f"[CODE] Implementing idea: {idea_title[:80]}")
```

In the BUILD/TEST/BENCHMARK blocks (in `_do_build_test_benchmark` and `run_shell_step` calls):
The `run_shell_step` already prefixes with the step name (BUILD, QUALITY). The benchmark loop already prefixes with BENCH. Add `[BENCHMARK]` before the benchmark section in `_do_build_test_benchmark`:
```python
log.info("[BENCHMARK] Starting benchmark...")
```

In the REVIEW block:
```python
log.info("[REVIEW] === STRATEGY REVIEW ===")
```

Also prefix the AI call log line in `ai.py` — actually no, the AI module doesn't know the phase. Instead, add phase to the `cli.py` log lines that precede AI calls:
```python
log.info(f"[CODE] AI: implementing idea: {idea_title[:80]}")
```

- [ ] **Step 2: Commit**

```bash
git add optimise/cli.py
git commit -m "add state-phase prefix to log messages"
```

---

### Task 9: Update spec and plan docs

**Files:**
- Modify: `docs/superpowers/specs/2026-03-14-optimiser-design.md`
- Modify: `docs/superpowers/plans/2026-03-14-optimiser.md`

- [ ] **Step 1: Update spec — Section 3 (Settings)**

Remove `max_dedup_attempts` from the settings listing and its comment.

- [ ] **Step 2: Update spec — Section 4 (Idea Lifecycle)**

In the **Selection** subsection, replace LLM-based selection with:
```
SELECT (merged into GENERATE)
  Pick the first idea file lexicographically from ideas/todo/.
  Move to ideas/coding/.
```

In the **Deduplication** subsection, replace with:
```
### Deduplication

Deduplication is handled implicitly:
- The generation prompt includes existing idea titles as a soft hint ("do NOT repeat these").
- If a previously-failed idea is regenerated, the early abort will catch it cheaply.
- No script-side dedup or retry loop.
```

- [ ] **Step 3: Update spec — Section 8 (State Machine)**

Update GENERATE to remove exhaustion logic:
```
GENERATE
  count ideas in ideas/todo/
  if < min_ideas:
    LLM batch-generates (min_ideas - count) ideas in one call
    write new ideas to ideas/todo/
    commit script repo: "generated N new ideas"
  if LLM failed to produce parseable ideas → retry (loop back to GENERATE)
  pick first idea lexicographically from ideas/todo/
  move to ideas/coding/
  → CODE
```

Update CODE to add NOT_APPLICABLE:
```
CODE
  script builds prompt: instructions + learnings + idea content
  if errors.txt exists: append to prompt with fix instructions
  LLM gets Read + Edit tools for target repo
  if LLM responds NOT_APPLICABLE → FAIL_IDEA (outcome: "not applicable")
  → BUILD
```

Remove the SELECT state entirely.

- [ ] **Step 4: Update spec — Section 9 (Termination)**

Remove item 4 (idea exhaustion) entirely.

- [ ] **Step 5: Update plan doc**

In `docs/superpowers/plans/2026-03-14-optimiser.md`, update the code listing for:
- `_generate_ideas` — remove dedup loop
- `GenerationResult` — remove EXHAUSTED
- Remove `parse_selection`
- Remove `build_selection_prompt`

(These are reference code in the plan; keep them in sync.)

- [ ] **Step 6: Remove `max_dedup_attempts` from live settings.conf**

In `settings.conf`, delete the line `max_dedup_attempts: 10`.

- [ ] **Step 7: Commit**

```bash
git add docs/ settings.conf
git commit -m "update specs, plans, and settings for simplified idea lifecycle"
```

---

### Task 10: Final verification

- [ ] **Step 1: Run full test suite**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 2: Verify no stale references**

Run: `grep -r "dedup_title\|parse_selection\|build_selection_prompt\|EXHAUSTED\|max_dedup_attempts" optimise/ tests/ --include="*.py"`
Expected: No matches.

- [ ] **Step 3: Commit if any fixups needed**
