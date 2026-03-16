"""Idea lifecycle management and file operations."""
import os
import re
import time


def sanitise_filename(name):
    """Sanitise an LLM-proposed idea filename.

    1. Strip any file extension.
    2. Replace characters not in [a-zA-Z0-9_-] with underscore.
    3. Append .md
    """
    # Strip extension if present
    base, ext = os.path.splitext(name)
    if ext:
        name = base
    # Replace disallowed characters
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    return name + ".md"


def create_idea(script_repo, raw_name, content):
    """Create an idea file in ideas/todo/.

    Prefixes the filename with a yyyy-mm-dd-hh-mm-ss timestamp so that
    lexicographic sorting reflects creation order. User files with numeric
    prefixes (e.g. 000-urgent) will sort before any timestamped file.

    Returns the absolute path to the created file.
    """
    filename = sanitise_filename(raw_name)
    ts = time.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{ts}-{filename}"
    path = os.path.join(script_repo, "ideas", "todo", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return path


def list_ideas(script_repo, subdir):
    """List idea filenames in ideas/<subdir>/. Returns list of filenames."""
    d = os.path.join(script_repo, "ideas", subdir)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".md"))


def move_idea(script_repo, filename, from_dir, to_dir):
    """Move an idea file between idea subdirectories."""
    src = os.path.join(script_repo, "ideas", from_dir, filename)
    dst = os.path.join(script_repo, "ideas", to_dir, filename)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)


def read_idea(script_repo, subdir, filename):
    """Read an idea file. Returns (title, body) where title is line 1."""
    path = os.path.join(script_repo, "ideas", subdir, filename)
    with open(path) as f:
        content = f.read()
    lines = content.split("\n", 1)
    title = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    return title, body


def append_outcome(script_repo, filename, outcome, commit_hash=None,
                   perf_summary=None, perf_table=None, explanation=None):
    """Append outcome to an idea file in ideas/done/."""
    path = os.path.join(script_repo, "ideas", "done", filename)
    with open(path, "a") as f:
        f.write(f"\noutcome: {outcome}\n")
        if commit_hash:
            f.write(f"commit: {commit_hash}\n")
        if perf_summary:
            f.write(f"{perf_summary}\n")
        if explanation:
            f.write(f"\n{explanation}\n")
        if perf_table:
            f.write(f"\n{perf_table}")


def all_idea_titles(script_repo):
    """Collect all idea titles from all idea subdirectories."""
    titles = []
    subdirs = ["todo", "coding", "testing", "done"]
    for subdir in subdirs:
        filenames = list_ideas(script_repo, subdir)
        for filename in filenames:
            title, _ = read_idea(script_repo, subdir, filename)
            titles.append(title)
    return titles



def clean_errors(script_repo):
    """Remove ideas/coding/errors.txt if it exists."""
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    if os.path.exists(path):
        os.remove(path)


def save_errors(script_repo, content):
    """Save error content to ideas/coding/errors.txt."""
    path = os.path.join(script_repo, "ideas", "coding", "errors.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
