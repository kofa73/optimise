#!/bin/bash
# Quality check: run darktable integration tests for diffuse module.
# Runs from the target repo root (passed as working directory by the optimiser).
set -e
export DARKTABLE_CLI=/home/developer/darktable-build/bin/darktable-cli
cd src/tests/integration
exec ./run.sh --disable-opencl --fast-fail \
    0086-diffuse \
    0087-diffuse-isotrope \
    0088-diffuse-gradient \
    0089-diffuse-mixed \
    0090-diffuse-sharpen
