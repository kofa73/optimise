# optimise/cli.py
"""CLI commands: init and run."""
import os
import logging

from optimise.settings import SETTINGS_TEMPLATE, INSTRUCTIONS_TEMPLATE, LEARNINGS_TEMPLATE

log = logging.getLogger("optimiser")


def do_init(directory):
    """Scaffold a new optimiser script repo.

    Creates settings.conf, instructions.md, learnings.md, and the
    ideas/ and perf-logs/ directory structure. Does not overwrite
    existing files.
    """
    files = {
        "settings.conf": SETTINGS_TEMPLATE,
        "instructions.md": INSTRUCTIONS_TEMPLATE,
        "learnings.md": LEARNINGS_TEMPLATE,
    }

    for filename, content in files.items():
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            log.info(f"  exists, skipping: {filename}")
        else:
            with open(path, "w") as f:
                f.write(content)
            log.info(f"  created: {filename}")

    dirs = [
        "ideas/todo",
        "ideas/coding",
        "ideas/testing",
        "ideas/done",
        "perf-logs",
    ]
    for d in dirs:
        path = os.path.join(directory, d)
        os.makedirs(path, exist_ok=True)
        log.info(f"  directory: {d}/")
