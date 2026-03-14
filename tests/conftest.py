# tests/conftest.py
import os
import subprocess
import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    """A temporary directory for test files."""
    return tmp_path


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repo with an initial commit."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    # Create initial commit on main
    marker = tmp_path / ".gitkeep"
    marker.write_text("")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


@pytest.fixture
def script_repo(tmp_path):
    """Create a script repo with the standard directory structure."""
    for d in ["ideas/todo", "ideas/coding", "ideas/testing", "ideas/done", "perf-logs"]:
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "learnings.md").write_text("## What works\n\n## What to avoid\n")
    (tmp_path / "instructions.md").write_text("Optimise the target for performance.\n")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path
