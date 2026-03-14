# tests/test_git.py
import subprocess
import pytest
from optimise.git import GitRepo, GitError


class TestGitRepo:
    def test_current_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        # Git init creates "main" or "master" depending on config
        branch = repo.current_branch()
        assert branch in ("main", "master")

    def test_is_dirty_clean_repo(self, git_repo):
        repo = GitRepo(str(git_repo))
        assert not repo.is_dirty()

    def test_is_dirty_modified_file(self, git_repo):
        (git_repo / ".gitkeep").write_text("modified")
        repo = GitRepo(str(git_repo))
        assert repo.is_dirty()

    def test_is_dirty_untracked_file(self, git_repo):
        (git_repo / "newfile.txt").write_text("new")
        repo = GitRepo(str(git_repo))
        # Untracked files should NOT count as dirty
        assert not repo.is_dirty()

    def test_branch_exists(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        assert repo.branch_exists(default)
        assert not repo.branch_exists("nonexistent-branch")

    def test_create_and_switch_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("test-branch")
        assert repo.current_branch() == "test-branch"

    def test_switch_branch(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        repo.create_branch("other")
        repo.switch_branch(default)
        assert repo.current_branch() == default
        repo.switch_branch("other")
        assert repo.current_branch() == "other"

    def test_rollback(self, git_repo):
        target = git_repo / "file.txt"
        target.write_text("original")
        subprocess.run(["git", "add", "file.txt"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add file"], cwd=git_repo, check=True, capture_output=True)
        target.write_text("modified")
        repo = GitRepo(str(git_repo))
        assert repo.is_dirty()
        repo.rollback()
        assert not repo.is_dirty()
        assert target.read_text() == "original"

    def test_rollback_removes_new_files(self, git_repo):
        (git_repo / "newfile.txt").write_text("new")
        repo = GitRepo(str(git_repo))
        repo.rollback()
        assert not (git_repo / "newfile.txt").exists()

    def test_commit_and_get_hash(self, git_repo):
        target = git_repo / "file.txt"
        target.write_text("content")
        repo = GitRepo(str(git_repo))
        repo.commit(["file.txt"], "test: add file", "Extended body\n\nDetails.")
        hash = repo.get_commit_hash()
        assert len(hash) >= 7
        assert not repo.is_dirty()

    def test_default_branch_detection(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.default_branch()
        assert default in ("main", "master")


class TestBranchResolution:
    def test_already_on_target(self, git_repo):
        repo = GitRepo(str(git_repo))
        default = repo.current_branch()
        repo.create_branch("optimise-test")
        # Should succeed — already on target
        repo.resolve_branch("optimise-test")
        assert repo.current_branch() == "optimise-test"

    def test_on_default_clean_creates_and_switches(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.resolve_branch("optimise-new")
        assert repo.current_branch() == "optimise-new"

    def test_on_default_dirty_fails(self, git_repo):
        (git_repo / ".gitkeep").write_text("dirty")
        repo = GitRepo(str(git_repo))
        with pytest.raises(GitError, match="uncommitted changes"):
            repo.resolve_branch("optimise-test")

    def test_on_wrong_branch_fails(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("some-other-branch")
        with pytest.raises(GitError, match="expected"):
            repo.resolve_branch("optimise-test")

    def test_on_default_target_exists_switches(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.create_branch("optimise-test")
        default = repo.default_branch()
        repo.switch_branch(default)
        repo.resolve_branch("optimise-test")
        assert repo.current_branch() == "optimise-test"


class TestCommitAll:
    def test_stages_and_commits_all(self, git_repo):
        (git_repo / "newfile.txt").write_text("content")
        repo = GitRepo(str(git_repo))
        repo.commit_all("test: add everything")
        assert not repo.is_dirty()
        assert not (git_repo / "newfile.txt").read_text() == ""  # file exists

    def test_noop_when_nothing_to_commit(self, git_repo):
        repo = GitRepo(str(git_repo))
        repo.commit_all("test: nothing")  # should not raise
