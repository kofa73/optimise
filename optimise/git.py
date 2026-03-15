# optimise/git.py
"""Git operations for target and script repositories."""
import os
import subprocess


class GitError(Exception):
    """Raised on git operation failures."""
    pass


class GitRepo:
    """Git operations on a single repository."""

    def __init__(self, path):
        self.path = path

    def _run(self, args, check=True, capture=True):
        """Run a git command in this repo."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.path,
            capture_output=capture,
            text=True,
        )
        if check and result.returncode != 0:
            raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result

    def current_branch(self):
        """Return the current branch name."""
        result = self._run(["rev-parse", "--abbrev-ref", "HEAD"])
        return result.stdout.strip()

    def default_branch(self):
        """Detect the default branch (main/master).

        Tries remote HEAD first, falls back to local branch names.
        """
        # Try remote HEAD
        result = self._run(["symbolic-ref", "refs/remotes/origin/HEAD"], check=False)
        if result.returncode == 0:
            ref = result.stdout.strip()
            return ref.split("/")[-1]
        # Fallback: check local branches
        for name in ("main", "master"):
            if self.branch_exists(name):
                return name
        # Last resort: current branch
        return self.current_branch()

    def is_dirty(self):
        """Check for uncommitted changes to tracked files."""
        result = self._run(["diff", "--quiet", "HEAD"], check=False)
        if result.returncode != 0:
            return True
        # Also check staged changes
        result = self._run(["diff", "--cached", "--quiet", "HEAD"], check=False)
        return result.returncode != 0

    def branch_exists(self, name):
        """Check if a local branch exists."""
        result = self._run(["rev-parse", "--verify", f"refs/heads/{name}"], check=False)
        return result.returncode == 0

    def create_branch(self, name):
        """Create a new branch and switch to it."""
        self._run(["checkout", "-b", name])

    def switch_branch(self, name):
        """Switch to an existing branch."""
        self._run(["checkout", name])

    def rollback(self):
        """Restore all tracked files to HEAD and remove untracked files."""
        self._run(["checkout", "HEAD", "--", "."])
        self._run(["clean", "-fd"])

    def changed_files(self):
        """Return list of tracked files with changes (staged or unstaged).

        Does NOT include untracked files.
        """
        result = self._run(["diff", "--name-only", "HEAD"], check=False)
        staged = self._run(["diff", "--cached", "--name-only", "HEAD"], check=False)
        files = set()
        for line in result.stdout.strip().splitlines():
            if line:
                files.add(line)
        for line in staged.stdout.strip().splitlines():
            if line:
                files.add(line)
        return sorted(files)

    def commit(self, files, title, body=None):
        """Stage specific files and commit.

        Args:
            files: list of relative file paths to stage
            title: commit message first line
            body: optional extended commit body (appended after blank line)
        """
        for f in files:
            self._run(["add", f])
        message = title
        if body:
            message = f"{title}\n\n{body}"
        self._run(["commit", "-m", message])

    def commit_changed(self, message, scope=None):
        """Stage and commit only changed tracked files under scope prefixes.

        Args:
            message: commit message
            scope: list of path prefixes to include (e.g. ["src/"]).
                   If None or empty, includes all changed files.
        """
        files = self.changed_files()
        if scope:
            files = [f for f in files
                     if any(f.startswith(s) for s in scope)]
        if not files:
            return
        for f in files:
            self._run(["add", f])
        self._run(["commit", "-m", message])

    def commit_all(self, message):
        """Stage all changes and commit."""
        self._run(["add", "-A"])
        # Check if there is anything to commit
        result = self._run(["diff", "--cached", "--quiet", "HEAD"], check=False)
        if result.returncode == 0:
            return  # Nothing to commit
        self._run(["commit", "-m", message])

    def get_commit_hash(self):
        """Return short hash of HEAD."""
        result = self._run(["rev-parse", "--short", "HEAD"])
        return result.stdout.strip()

    def resolve_branch(self, target_branch):
        """Ensure we are on the target branch per the spec's branch resolution logic.

        If on default branch and clean: create target if needed, switch.
        If on target: OK.
        Otherwise: raise GitError.
        """
        current = self.current_branch()

        if current == target_branch:
            return

        default = self.default_branch()
        if current == default:
            if self.is_dirty():
                raise GitError(
                    f"Repository at {self.path} has uncommitted changes on "
                    f"{default}. Please clean up first."
                )
            if not self.branch_exists(target_branch):
                self.create_branch(target_branch)
            else:
                self.switch_branch(target_branch)
        else:
            raise GitError(
                f"Repository at {self.path} is on branch '{current}', "
                f"expected '{target_branch}' or '{default}'. Please clean up first."
            )
