# Automatic Ideas Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automate generation and review of ideas to trigger precisely when the 'todo' list is empty.

**Architecture:** 
1. Replace `min_ideas` and `review_frequency` with `idea_generation_batch_size`.
2. During the `GENERATE` state, if there are no ideas left in the `todo` directory, we perform a review (only if completed ideas exist in `done`), and then generate a batch of ideas defined by `idea_generation_batch_size`.
3. We remove periodic reviews from the `CODE` and `TEST` execution states.

**Tech Stack:** Python, pytest

---

### Task 1: Update Settings

**Files:**
- Modify: `optimise/settings.py`
- Modify: `settings.conf`
- Test: `tests/test_settings.py`

**Step 1: Write the failing tests**

```python
# In tests/test_settings.py:
# Update `_make_valid_settings` to replace:
#   "review_frequency": "3",
#   "min_ideas": "5",
# With:
#   "idea_generation_batch_size": "5",

# Update assertions in `TestValidateSettings` tests if any specifically rely on those keys.
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings.py -v`
Expected: FAIL due to missing keys or validation errors.

**Step 3: Write minimal implementation**

In `optimise/settings.py`:
- Remove `"review_frequency"` and `"min_ideas"` from `_INT_KEYS`.
- Add `"idea_generation_batch_size"` to `_INT_KEYS`.
- Update `SETTINGS_TEMPLATE` to replace `review_frequency` and `min_ideas` parameters with `idea_generation_batch_size: 5`.

In `settings.conf`:
- Remove `review_frequency: 3` and `min_ideas: 5`.
- Add `idea_generation_batch_size: 5`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add optimise/settings.py settings.conf tests/test_settings.py
git commit -m "feat: replace min_ideas/review_frequency with idea_generation_batch_size in settings"
```

---

### Task 2: Update CLI Idea Generation Logic

**Files:**
- Modify: `optimise/cli.py`
- Test: `tests/test_cli.py`

**Step 1: Write the failing test**

In `tests/test_cli.py`:
- In `TestGenerateIdeas`, update tests to use `{"idea_generation_batch_size": 1}` instead of `{"min_ideas": 1}`.
- Change `test_no_generation_needed_returns_ok` test to verify that `todo_count` math is no longer performed by `_generate_ideas` directly (if checked) or we can just delete/modify tests asserting that `_generate_ideas` skips generation when `len(todo) >= min_ideas`. `_generate_ideas` will fundamentally perform generation regardless of `todo_count`.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::TestGenerateIdeas -v`
Expected: FAIL due to KeyErrors or incorrect parameters passed.

**Step 3: Write minimal implementation**

In `optimise/cli.py` in `_generate_ideas`:
```python
    needed = settings["idea_generation_batch_size"]
    
    if needed <= 0:
        return GenerationResult.OK
```
(Remove all the `todo_count` math inside `_generate_ideas`).

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::TestGenerateIdeas -v`
Expected: PASS

**Step 5: Commit**

```bash
git add optimise/cli.py tests/test_cli.py
git commit -m "feat: _generate_ideas uses idea_generation_batch_size directly"
```

---

### Task 3: Update CLI Event Loop (GENERATE State and Reviews)

**Files:**
- Modify: `optimise/cli.py`

**Step 1: Write the minimal implementation**

In `optimise/cli.py` inside `do_run`:

Find `if state == StartupState.GENERATE:`:
```python
        if state == StartupState.GENERATE:
            todo_files = list_ideas(directory, "todo")
            
            if not todo_files:
                # 1. Review
                if list_ideas(directory, "done"):
                    _do_review(directory, script_git, ai, instructions, target_repo_path)
                
                # 2. Generate
                todo_before = 0
                gen_result = _generate_ideas(
                    directory, settings, ai, target_repo_path,
                    instructions, target_files,
                )
                todo_after = len(list_ideas(directory, "todo"))
                if todo_after > todo_before:
                    script_git.commit_all(f"generated {todo_after - todo_before} new ideas")
                
                if gen_result == GenerationResult.LLM_FAILURE:
                    log.warning("[GENERATE] All LLM providers failed — "
                                "will retry after cooldown")
                    continue
                
                # Re-fetch after generation
                todo_files = list_ideas(directory, "todo")
```

Also, remove the `_do_review` calls logic inside `StartupState.CODE` block:
```python
            # Check review
            if iteration % settings["review_frequency"] == 0:
                _do_review(directory, script_git, ai, instructions, target_repo_path)
```
Remove the exact same lines from `StartupState.TEST` block.

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v` to ensure we didn't break other tests.

**Step 3: Commit**

```bash
git add optimise/cli.py
git commit -m "feat: generate ideas and review only when todo queue is empty"
```
