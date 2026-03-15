# optimise/prompts.py
"""Prompt builders for each LLM role."""


def build_generation_prompt(instructions, learnings, existing_titles, count, target_files):
    """Build prompt for batch idea generation.

    The LLM should read the target files to understand the code, then propose
    `count` optimisation ideas. Each idea needs a filename, title, and description.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)
    existing = "\n".join(f"- {t}" for t in existing_titles) if existing_titles else "(none yet)"

    return f"""\
# Instructions

{instructions}

# Target files

Read these files to understand the code: {targets}

# Learnings from past experiments

{learnings}

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
"""



def build_implementation_prompt(instructions, learnings, idea_content, target_files, errors):
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

1. Use the Read tool to read the target files. Use Edit to make changes.
2. Make ONLY the changes described in the idea. Do not refactor other code.

3. **YOU MUST NOT RUN ANY BUILD COMMANDS. THIS IS FORBIDDEN.**
4. **YOU MUST NOT RUN ANY TEST COMMANDS. THIS IS PROHIBITED.**
5. **YOU MUST NOT RUN ANY BENCHMARK COMMANDS. YOU WILL BE PENALIZED.**
6. **YOU MUST NEVER USE SHELL/BASH TOOLS TO EXECUTE ANYTHING.**
7. **IF YOU ATTEMPT TO BUILD, TEST, OR BENCHMARK, THE SESSION WILL BE TERMINATED.**

The orchestrator script handles ALL building, testing, and benchmarking
after you return control. Your ONLY job is to edit the source files.

When done editing, output a brief summary of what you changed.
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
