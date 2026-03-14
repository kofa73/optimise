#!/usr/bin/env python3
"""Optimiser — automated performance optimisation via LLM."""
import argparse
import logging
import os
import sys

from optimise.cli import do_init


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Automated performance optimisation via LLM",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold a new optimiser workspace")
    init_parser.add_argument("--dir", default=".",
                            help="Directory to scaffold (default: current)")

    # run command
    run_parser = subparsers.add_parser("run", help="Run the optimisation loop")
    run_parser.add_argument("--dir", default=".",
                           help="Script repo directory (default: current)")

    args = parser.parse_args()

    if args.command == "init":
        directory = os.path.abspath(args.dir)
        print(f"Initialising optimiser workspace in {directory}")
        do_init(directory)
        print("Done. Edit settings.conf and instructions.md, then run: python optimise.py run")
    elif args.command == "run":
        print("Run command not yet implemented.")
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
