# tests/test_prompts.py
import pytest
from optimise.prompts import (
    build_generation_prompt,
    build_selection_prompt,
    build_implementation_prompt,
    build_review_prompt,
)


class TestGenerationPrompt:
    def test_includes_instructions(self):
        prompt = build_generation_prompt(
            instructions="Optimise diffuse.c",
            learnings="## What works\n- inlining",
            existing_titles=["Title A"],
            count=3,
            target_files=["src/main.c"],
        )
        assert "Optimise diffuse.c" in prompt
        assert "inlining" in prompt
        assert "Title A" in prompt
        assert "3" in prompt

    def test_includes_target_files(self):
        prompt = build_generation_prompt(
            instructions="Optimise",
            learnings="",
            existing_titles=[],
            count=2,
            target_files=["src/a.c", "src/b.c"],
        )
        assert "src/a.c" in prompt
        assert "src/b.c" in prompt


class TestSelectionPrompt:
    def test_includes_all_ideas(self):
        ideas = {"idea-a.md": "Title A\n\nBody A", "idea-b.md": "Title B\n\nBody B"}
        prompt = build_selection_prompt(ideas)
        assert "idea-a.md" in prompt
        assert "Title A" in prompt
        assert "idea-b.md" in prompt


class TestImplementationPrompt:
    def test_includes_idea_and_instructions(self):
        prompt = build_implementation_prompt(
            instructions="Optimise diffuse.c",
            learnings="## What works\n- inlining",
            idea_content="Remove redundant loop\n\nDetails here",
            target_files=["src/diffuse.c"],
            errors=None,
        )
        assert "Optimise diffuse.c" in prompt
        assert "Remove redundant loop" in prompt
        assert "src/diffuse.c" in prompt

    def test_has_multiple_prohibitions(self):
        prompt = build_implementation_prompt(
            instructions="", learnings="",
            idea_content="idea",
            target_files=["f.c"],
            errors=None,
        )
        # Must have at least 3 separate prohibitions
        prohibitions = [line for line in prompt.split("\n")
                       if "MUST NOT" in line or "FORBIDDEN" in line or "PENALIZED" in line
                       or "PROHIBITED" in line or "NEVER" in line]
        assert len(prohibitions) >= 3

    def test_includes_errors_when_present(self):
        prompt = build_implementation_prompt(
            instructions="", learnings="",
            idea_content="idea",
            target_files=["f.c"],
            errors="error: undefined reference to foo",
        )
        assert "undefined reference to foo" in prompt
        assert "fix" in prompt.lower() or "Fix" in prompt


class TestReviewPrompt:
    def test_includes_done_ideas(self):
        done_ideas = {"a.md": "Title A\n\nBody\noutcome: improvement",
                      "b.md": "Title B\n\nBody\noutcome: build failure"}
        prompt = build_review_prompt(
            instructions="Optimise",
            done_ideas=done_ideas,
        )
        assert "Title A" in prompt
        assert "improvement" in prompt
        assert "build failure" in prompt
        assert "learnings.md" in prompt
