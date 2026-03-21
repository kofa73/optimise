# tests/test_state.py
import pytest
import os
from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \
    read_idea, append_outcome, all_idea_titles, clean_errors, save_errors


class TestSanitiseFilename:
    def test_clean_name(self):
        assert sanitise_filename("precompute-half_anisotropy") == "precompute-half_anisotropy.md"

    def test_strips_extension(self):
        assert sanitise_filename("my-idea.txt") == "my-idea.md"

    def test_strips_md_extension(self):
        assert sanitise_filename("my-idea.md") == "my-idea.md"

    def test_replaces_spaces(self):
        assert sanitise_filename("my great idea") == "my_great_idea.md"

    def test_replaces_special_chars(self):
        # The implementation uses re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
        # "idea: improve (speed) by 50%!"
        # ":" -> "_"
        # " " -> "_"
        # "(" -> "_"
        # ")" -> "_"
        # " " -> "_"
        # "%" -> "_"
        # "!" -> "_"
        assert sanitise_filename("idea: improve (speed) by 50%!") == "idea__improve__speed__by_50__.md"

    def test_complex_llm_output(self):
        name = "precompute half anisotropy outside loop, to improve gradient calculation speed.txt"
        result = sanitise_filename(name)
        # " " -> "_"
        # "," -> "_"
        assert result == "precompute_half_anisotropy_outside_loop__to_improve_gradient_calculation_speed.md"
        # Verify only allowed chars (plus .md extension)
        stem = result[:-3]
        assert all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in stem)


class TestCreateIdea:
    def test_creates_file_in_todo(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "my-idea", "Improve loop performance\n\nDetails here.")
        assert path.endswith(".md")
        assert "ideas/todo/" in path
        with open(path) as f:
            assert f.read() == "Improve loop performance\n\nDetails here."

    def test_sanitises_filename(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "bad name with spaces.txt", "Title\n\nBody")
        assert "bad_name_with_spaces.md" in path

    def test_prefixes_with_timestamp(self, tmp_path):
        """Generated ideas get a yyyy-mm-dd-hh-mm-ss prefix for ordering."""
        import re
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "z-index-optimisation", "Title\n\nBody")
        filename = os.path.basename(path)
        # Must start with a timestamp pattern
        assert re.match(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-", filename), \
            f"Expected timestamp prefix, got: {filename}"
        assert filename.endswith("z-index-optimisation.md")

    def test_timestamp_ordering(self, tmp_path):
        """Ideas created later sort after earlier ones."""
        import time
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        create_idea(str(tmp_path), "z-idea", "First\n\nBody")
        time.sleep(1.1)  # ensure different second
        create_idea(str(tmp_path), "a-idea", "Second\n\nBody")
        ideas = list_ideas(str(tmp_path), "todo")
        # z-idea was created first, so it should sort before a-idea
        assert "z-idea" in ideas[0]
        assert "a-idea" in ideas[1]

    def test_ordinal_prefix(self, tmp_path):
        """With ordinal=1, filename gets '001-' prefix before timestamp."""
        import re
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "my-idea", "Title\n\nBody", ordinal=1)
        filename = os.path.basename(path)
        assert re.match(r"001-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-my-idea\.md$", filename), \
            f"Expected 001-timestamp-my-idea.md, got: {filename}"

    def test_ordinal_prefix_three_digits(self, tmp_path):
        """Ordinal 42 becomes '042-'."""
        import re
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "idea-x", "Title\n\nBody", ordinal=42)
        filename = os.path.basename(path)
        assert filename.startswith("042-"), f"Expected 042- prefix, got: {filename}"

    def test_no_ordinal_no_prefix(self, tmp_path):
        """Without ordinal, filename starts with timestamp (backward compat)."""
        import re
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        path = create_idea(str(tmp_path), "idea-y", "Title\n\nBody")
        filename = os.path.basename(path)
        assert re.match(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-idea-y\.md$", filename), \
            f"Expected timestamp-idea-y.md, got: {filename}"

    def test_user_prefix_sorts_before_timestamp(self, tmp_path):
        """User 000- prefix sorts before any timestamp-prefixed idea."""
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        create_idea(str(tmp_path), "some-idea", "Generated\n\nBody")
        # Manually create a user-prioritized idea (no timestamp)
        (todo / "000-urgent.md").write_text("Urgent idea\n\nDo first.")
        ideas = list_ideas(str(tmp_path), "todo")
        assert ideas[0] == "000-urgent.md"


class TestListIdeas:
    def test_lists_todo_ideas(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        (todo / "idea-a.md").write_text("Idea A title\n\nBody")
        (todo / "idea-b.md").write_text("Idea B title\n\nBody")
        result = list_ideas(str(tmp_path), "todo")
        assert sorted(result) == ["idea-a.md", "idea-b.md"]

    def test_empty_directory(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        assert list_ideas(str(tmp_path), "todo") == []


class TestMoveIdea:
    def test_moves_between_directories(self, tmp_path):
        for d in ["ideas/todo", "ideas/coding"]:
            (tmp_path / d).mkdir(parents=True)
        src = tmp_path / "ideas" / "todo" / "my-idea.md"
        src.write_text("content")
        move_idea(str(tmp_path), "my-idea.md", "todo", "coding")
        assert not src.exists()
        dst = tmp_path / "ideas" / "coding" / "my-idea.md"
        assert dst.exists()
        assert dst.read_text() == "content"


class TestReadIdea:
    def test_reads_title_and_body(self, tmp_path):
        todo = tmp_path / "ideas" / "todo"
        todo.mkdir(parents=True)
        (todo / "idea.md").write_text("The title line\n\nThe body text.\nMore body.")
        title, body = read_idea(str(tmp_path), "todo", "idea.md")
        assert title == "The title line"
        assert "The body text." in body


class TestAppendOutcome:
    def test_appends_success(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        append_outcome(str(tmp_path), "idea.md", "improvement",
                       commit_hash="abc123",
                       perf_summary="Reduced sum(user) from 10.0s to 9.0s (~10.0% improvement)")
        content = (done / "idea.md").read_text()
        assert "outcome: improvement" in content
        assert "commit: abc123" in content
        assert "Reduced sum(user)" in content

    def test_appends_failure(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        append_outcome(str(tmp_path), "idea.md", "build failure")
        content = (done / "idea.md").read_text()
        assert "outcome: build failure" in content
        assert "commit:" not in content

    def test_appends_perf_table(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        perf_table = "# Individual timings\n| user |\n| ---- |\n| 1.000 |\n"
        append_outcome(str(tmp_path), "idea.md", "performance regression",
                       perf_table=perf_table)
        content = (done / "idea.md").read_text()
        assert "outcome: performance regression" in content
        assert "# Individual timings" in content
        assert "| 1.000 |" in content

    def test_appends_explanation(self, tmp_path):
        done = tmp_path / "ideas" / "done"
        done.mkdir(parents=True)
        (done / "idea.md").write_text("Title\n\nBody")
        append_outcome(str(tmp_path), "idea.md", "not applicable",
                       explanation="The code already uses a similar optimisation.")
        content = (done / "idea.md").read_text()
        assert "outcome: not applicable" in content
        assert "\nThe code already uses a similar optimisation.\n" in content


class TestAllIdeaTitles:
    def test_collects_from_all_dirs(self, tmp_path):
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (tmp_path / d).mkdir(parents=True)
        (tmp_path / "ideas" / "todo" / "a.md").write_text("Title A\n\nBody")
        (tmp_path / "ideas" / "done" / "b.md").write_text("Title B\n\nBody")
        titles = all_idea_titles(str(tmp_path))
        assert set(titles) == {"Title A", "Title B"}



class TestCleanErrors:
    def test_removes_existing_file(self, tmp_path):
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        (coding / "errors.txt").write_text("some error")
        clean_errors(str(tmp_path))
        assert not (coding / "errors.txt").exists()

    def test_no_error_if_missing(self, tmp_path):
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        clean_errors(str(tmp_path))  # should not raise


class TestSaveErrors:
    def test_writes_error_file(self, tmp_path):
        coding = tmp_path / "ideas" / "coding"
        coding.mkdir(parents=True)
        save_errors(str(tmp_path), "error: undefined reference")
        assert (coding / "errors.txt").read_text() == "error: undefined reference"
