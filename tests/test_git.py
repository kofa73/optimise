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

    def test_is_dirty_with_scope(self, git_repo):
        (git_repo / "src").mkdir()
        (git_repo / "tests").mkdir()
        (git_repo / "src" / "main.c").write_text("v1")
        (git_repo / "tests" / "test.c").write_text("v1")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=git_repo, check=True, capture_output=True)
        
        (git_repo / "src" / "main.c").write_text("dirty")
        repo = GitRepo(str(git_repo))
        
        dirty_src = repo.is_dirty(scope=["src/"])
        dirty_tests = repo.is_dirty(scope=["tests/"])
        
        assert dirty_src
        assert "src/main.c" in dirty_src
        assert not dirty_tests

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


class TestChangedFiles:
    def test_returns_modified_tracked_files(self, git_repo):
        (git_repo / ".gitkeep").write_text("modified")
        repo = GitRepo(str(git_repo))
        assert repo.changed_files() == [".gitkeep"]

    def test_excludes_untracked_files(self, git_repo):
        (git_repo / "untracked.txt").write_text("new")
        repo = GitRepo(str(git_repo))
        assert repo.changed_files() == []

    def test_includes_new_tracked_files(self, git_repo):
        (git_repo / "added.txt").write_text("new")
        subprocess.run(["git", "add", "added.txt"], cwd=git_repo,
                        check=True, capture_output=True)
        repo = GitRepo(str(git_repo))
        assert "added.txt" in repo.changed_files()

    def test_empty_on_clean_repo(self, git_repo):
        repo = GitRepo(str(git_repo))
        assert repo.changed_files() == []


class TestCommitChanged:
    def test_scope_limits_to_matching_prefix(self, git_repo):
        """Only files under the scope prefix are committed."""
        (git_repo / "src").mkdir()
        (git_repo / "tests").mkdir()
        (git_repo / "src" / "main.c").write_text("code")
        (git_repo / "tests" / "check.c").write_text("test")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=git_repo, check=True, capture_output=True)
        (git_repo / "src" / "main.c").write_text("optimised")
        (git_repo / "tests" / "check.c").write_text("modified test")
        repo = GitRepo(str(git_repo))
        repo.commit_changed("optimise", scope=["src/"])
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=git_repo, capture_output=True, text=True,
        )
        assert "tests/check.c" in result.stdout
        assert "src/main.c" not in result.stdout

    def test_noop_when_nothing_in_scope(self, git_repo):
        """No commit when no changed files match scope."""
        (git_repo / ".gitkeep").write_text("modified")
        repo = GitRepo(str(git_repo))
        repo.commit_changed("nothing to do", scope=["src/"])
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=git_repo, capture_output=True, text=True,
        )
        assert "nothing to do" not in result.stdout

    def test_no_scope_commits_all_changed(self, git_repo):
        """Without scope, commits all changed tracked files."""
        (git_repo / ".gitkeep").write_text("modified")
        repo = GitRepo(str(git_repo))
        repo.commit_changed("commit all changes")
        assert not repo.is_dirty()


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


class TestCommitExists:
    def test_returns_true_for_head(self, git_repo):
        repo = GitRepo(str(git_repo))
        assert repo.commit_exists("HEAD")

    def test_returns_false_for_invalid_commit(self, git_repo):
        repo = GitRepo(str(git_repo))
        assert not repo.commit_exists("invalid-hash-123")


class TestGetFileAtCommit:
    def test_returns_file_content(self, git_repo):
        target = git_repo / "file.txt"
        target.write_text("v1")
        subprocess.run(["git", "add", "file.txt"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=git_repo, check=True, capture_output=True)
        v1_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git_repo, capture_output=True, text=True).stdout.strip()
        
        target.write_text("v2")
        subprocess.run(["git", "add", "file.txt"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v2"], cwd=git_repo, check=True, capture_output=True)
        
        repo = GitRepo(str(git_repo))
        assert repo.get_file_at_commit(v1_hash, "file.txt") == "v1"
        assert repo.get_file_at_commit("HEAD", "file.txt") == "v2"

    def test_raises_if_file_not_found_in_commit(self, git_repo):
        repo = GitRepo(str(git_repo))
        with pytest.raises(GitError):
            repo.get_file_at_commit("HEAD", "missing.txt")


class TestRollbackScope:
    def test_rolls_back_only_specified_scope(self, git_repo):
        (git_repo / "src").mkdir()
        (git_repo / "tests").mkdir()
        (git_repo / "src" / "main.c").write_text("v1")
        (git_repo / "tests" / "test.c").write_text("v1")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=git_repo, check=True, capture_output=True)
        
        (git_repo / "src" / "main.c").write_text("dirty")
        (git_repo / "tests" / "test.c").write_text("dirty")
        repo = GitRepo(str(git_repo))
        
        repo.rollback_scope(scope=["src/"])
        assert (git_repo / "src" / "main.c").read_text() == "v1" # Rolled back
        assert (git_repo / "tests" / "test.c").read_text() == "dirty" # Not rolled back

