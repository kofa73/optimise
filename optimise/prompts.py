# optimise/prompts.py
"""Prompt builders for each LLM role."""


def _targeting_section(targeting, focus_line):
    """Build the instance targeting prompt section, or empty string."""
    if not targeting:
        return ""
    return f"""
# Instance targeting

The benchmark runs {targeting['instance_count']} instances of the "{targeting['module_name']}" module. \
Instance {targeting['index']} ("{targeting['label']}") has improved the least \
({targeting['improvement_pct']:+.1f}% vs average {targeting['avg_improvement_pct']:+.1f}%).

Baseline: {targeting['baseline_user']:.3f}s, current best: {targeting['current_user']:.3f}s

Parameters for this instance:
{targeting['params_text']}

{focus_line}
"""


def build_generation_prompt(instructions, learnings, existing_titles, count, target_files,
                            targeting=None):
    """Build prompt for batch idea generation.

    The LLM should read the target files to understand the code, then propose
    `count` optimisation ideas. Each idea needs a filename, title, and description.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)
    existing = "\n".join(f"- {t}" for t in existing_titles) if existing_titles else "(none yet)"

    targeting_block = _targeting_section(
        targeting, "Focus your ideas on code paths that would improve performance for these parameters.")

    return f"""\
# Instructions

{instructions}

# Target files

Read these files to understand the code: {targets}

# Learnings from past experiments

{learnings}
{targeting_block}
# Existing ideas (do NOT repeat these)

{existing}

# Your task

Generate exactly {count} new optimisation ideas for the target files.

For EACH idea, output in this exact format (with the triple-dash separator between ideas):

---
FILENAME: a-brief-descriptive-name
TITLE: one line suitable as a git commit message
DESCRIPTION:
A short paragraph explaining what to change and why it should improve performance.
---

Rules:
- Filenames must use only [a-zA-Z0-9_-], no extension
- Each idea must be genuinely different from the existing ideas listed above
- Focus on ideas that are likely to succeed based on the learnings
- List ideas in descending order of expected improvement (most impactful first, least impactful last)
"""



def build_implementation_prompt(instructions, learnings, idea_content, target_files, errors,
                                targeting=None):
    """Build prompt for implementing an optimisation idea.

    Contains at least three separate, strong prohibitions against running
    builds/tests/benchmarks.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)

    error_block = ""
    if errors:
        error_block = f"""
## PREVIOUS ATTEMPT FAILED

The previous attempt to implement this idea resulted in errors.
You MUST fix these errors. Here is the build/test output:

```
{errors}
```
"""

    targeting_block = _targeting_section(
        targeting, "Prioritise code paths exercised by these parameters.")

    return f"""\
# Instructions

{instructions}

# Learnings from past experiments

{learnings}
{targeting_block}
# Your task

Implement this optimisation idea by editing the target files ({targets}):

{idea_content}

{error_block}

## CRITICAL RULES — READ EVERY ONE

1. Read the target files and assess whether this idea is still applicable
   given the current state of the code. If the optimisation has already been applied,
   or the code structure has changed making it infeasible, respond with exactly
   `NOT_APPLICABLE` on the first line, followed by a brief explanation. Do nothing else.
2. Use Edit to make ONLY the changes described in the idea. Do not refactor other code.

4. **YOU MUST NOT RUN ANY BUILD COMMANDS. THIS IS FORBIDDEN.**
5. **YOU MUST NOT RUN ANY TEST COMMANDS. THIS IS PROHIBITED.**
6. **YOU MUST NOT RUN ANY BENCHMARK COMMANDS. YOU WILL BE PENALIZED.**
7. **YOU MUST NEVER USE SHELL/BASH TOOLS TO EXECUTE ANYTHING.**
8. **IF YOU ATTEMPT TO BUILD, TEST, OR BENCHMARK, THE SESSION WILL BE TERMINATED.**

The orchestrator script handles ALL building, testing, and benchmarking
after you return control. Your ONLY job is to edit the source files.

When done editing, output a brief summary of what you changed.
"""


def build_code_review_prompt(instructions, diff, idea_content):
    """Build prompt for automated code review of LLM-generated changes.

    Uses the "normal" (cheaper) LLM tier. Checks a narrow, hardcoded
    checklist rather than doing a general code review.
    """
    return f"""\
# Code Review

You are reviewing code changes made by another AI. Your job is to check
a specific checklist — nothing else. Do not suggest improvements beyond
the checklist.

## Project Instructions (for context)

{instructions}

## Idea Being Implemented

{idea_content}

## Diff to Review

```diff
{diff}
```

## Checklist

Check ONLY these items:

1. **Stale comments**: Are there comments in the diff that no longer describe the code
   they annotate? This includes comments left behind after removing or changing code.
2. **Macro misuse**: Were large macros introduced? Avoid giant body macros, but do
   not approve a refactor just because it replaced a macro with inline functions.
3. **Unswitched duplication**: Is there duplicated code from loop unswitching that
   should be factored into separate `always_inline` helper functions?
4. **Specialization-boundary regressions**: Did the change replace specialized outer
   dispatch or macro expansion with one generic helper that now contains `DT_OMP_FOR()`
   or the parallel row loop while taking hot-path flags as ordinary parameters? Did it
   collapse many unswitched entry paths into one runtime-branching loop? Reject such
   changes. The safe pattern is shared `always_inline` inner helpers plus small
   specialized wrapper functions at the parallel-loop boundary.
5. **OpenCL contamination**: Were any `_cl` functions or OpenCL-only code paths
   modified? The CPU benchmark does not test those paths, so they must not be changed
   unless the change is trivially required by a shared-code refactor.

## Response Format

- If ALL checks pass, respond with exactly `LGTM` on the first line. Nothing else.
- If ANY check fails, describe the specific issue(s) found. Be concise and actionable.

**Do not edit any files. Do not run any commands. Only provide your review verdict.**
"""


def build_review_prompt(instructions, done_ideas):
    """Build prompt for periodic strategy review.

    The LLM gets Read+Edit on the script repo to update learnings.md.
    """
    sections = []
    for filename, content in sorted(done_ideas.items()):
        sections.append(f"## {filename}\n\n{content}")
    ideas_text = "\n\n".join(sections)

    return f"""\
# Instructions

{instructions}

# Completed experiments

{ideas_text}

# Your task

Review all completed experiments above. Update `learnings.md` using the
Read and Edit tools. The file should have two sections:

## What works
Bullet points describing patterns that consistently lead to successful
optimisations, with evidence from the experiments.

## What to avoid
Bullet points describing patterns that consistently fail, with reasons.

Keep it concise: 10-20 bullet points total. You may update, remove, or
add entries based on the evidence. Remove entries that are contradicted
by newer evidence.
"""
