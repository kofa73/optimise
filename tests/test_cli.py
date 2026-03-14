# tests/test_cli.py
import os
import pytest
from optimise.cli import do_init


class TestInit:
    def test_creates_settings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").exists()
        content = (tmp_path / "settings.conf").read_text()
        assert "target_repo:" in content
        assert "build_cmd:" in content

    def test_creates_instructions(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "instructions.md").exists()

    def test_creates_learnings(self, tmp_path):
        do_init(str(tmp_path))
        assert (tmp_path / "learnings.md").exists()
        content = (tmp_path / "learnings.md").read_text()
        assert "## What works" in content
        assert "## What to avoid" in content

    def test_creates_directories(self, tmp_path):
        do_init(str(tmp_path))
        for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
            assert (tmp_path / d).is_dir()

    def test_idempotent_does_not_overwrite(self, tmp_path):
        do_init(str(tmp_path))
        # Modify settings
        (tmp_path / "settings.conf").write_text("custom content")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom content"

    def test_creates_missing_files_only(self, tmp_path):
        # Create settings but not learnings
        (tmp_path / "settings.conf").write_text("custom")
        do_init(str(tmp_path))
        assert (tmp_path / "settings.conf").read_text() == "custom"
        assert (tmp_path / "learnings.md").exists()
