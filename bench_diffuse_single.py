#!/usr/bin/env python3
"""Single-run benchmark for diffuse module. Outputs user=X.XXX per instance.

Designed for use with the optimiser's convergence loop — runs darktable-cli
once and prints one line per diffuse instance.
"""
import os
import re
import subprocess
import sys
import glob

BIN = os.path.expanduser("~/darktable-build/bin/darktable-cli")

if len(sys.argv) < 3:
    print("Usage: bench_diffuse_single.py <image> <sidecar>", file=sys.stderr)
    sys.exit(1)

IMAGE = sys.argv[1]
XMP = sys.argv[2]
OUT_DIR = "/tmp/dt-bench-out"
CONFIG_DIR = "/tmp/darktable-perftest/"

cmd = [
    BIN, IMAGE, XMP, OUT_DIR,
    "--core", "-d", "perf",
    "--disable-opencl",
    "--configdir", CONFIG_DIR,
    "--cachedir", "/tmp/dtcache",
]

os.makedirs(OUT_DIR, exist_ok=True)

result = subprocess.run(cmd, capture_output=True, text=True)
output = result.stdout + result.stderr

pattern = re.compile(
    r"took ([\d.]+) secs \(([\d.]+) CPU\).*processed `(diffuse[^']*)'",
)

found = 0
for line in output.splitlines():
    if "processed" in line and "diffuse" in line and "on CPU" in line:
        m = pattern.search(line)
        if m:
            user = m.group(1)
            cpu = m.group(2)
            print(f"user={user}, cpu={cpu}")
            found += 1

# Clean up output files
for f in glob.glob(os.path.join(OUT_DIR, "*.jpg")):
    try:
        os.remove(f)
    except OSError:
        pass

EXPECTED_INSTANCES = 21

if found == 0:
    print("ERROR: no diffuse instances found in output", file=sys.stderr)
    sys.exit(1)
elif found != EXPECTED_INSTANCES:
    print(f"WARNING: expected {EXPECTED_INSTANCES} diffuse instances, got {found}",
          file=sys.stderr)
    sys.exit(1)
