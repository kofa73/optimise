# tests/test_state.py
import pytest
import os
from optimise.state import sanitise_filename, create_idea, list_ideas, move_idea, \
    read_idea, append_outcome, all_idea_titles, dedup_title, clean_errors, save_errors


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


class TestAllIdeaTitles:
    def test_collects_from_all_dirs(self, tmp_path):
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done"]:
            (tmp_path / d).mkdir(parents=True)
        (tmp_path / "ideas" / "todo" / "a.md").write_text("Title A\n\nBody")
        (tmp_path / "ideas" / "done" / "b.md").write_text("Title B\n\nBody")
        titles = all_idea_titles(str(tmp_path))
        assert set(titles) == {"Title A", "Title B"}


class TestDedupTitle:
    def test_exact_match_is_duplicate(self):
        assert dedup_title("My Idea", ["My Idea", "Other"]) is True

    def test_case_insensitive(self):
        assert dedup_title("my idea", ["My Idea"]) is True

    def test_no_match(self):
        assert dedup_title("New Idea", ["Old Idea"]) is False

    def test_empty_list(self):
        assert dedup_title("Idea", []) is False


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
