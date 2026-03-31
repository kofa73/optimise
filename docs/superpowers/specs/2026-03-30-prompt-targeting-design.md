# Prompt Targeting for Least-Improved Instance

Pass instance-specific context (label, decoded parameters, timing gap) into the generation and implementation LLM prompts when `targeting_mode` is `least_improved_instance`, so the LLM knows which module instance to focus on.

**Builds on:** Instance targeting spec (2026-03-23), which implemented evaluation-layer targeting but left prompt enrichment as a dependency on config/sidecar work.

---

## 1. New Mandatory Settings

Three new mandatory keys in `settings.conf`:

```
bench_image: test-data/DSC_9034.NEF
bench_sidecar: test-data/DSC_9034.NEF.xmp
module_name: diffuse
```

- `bench_image`: path to the benchmark input image, relative to the script repo directory. Resolved to absolute before use. Passed as `sys.argv[1]` to the benchmark script.
- `bench_sidecar`: path to the XMP sidecar file, relative to the script repo directory. Resolved to absolute before use. Passed as `sys.argv[2]` to the benchmark script. Also used by the optimiser for XMP parsing.
- `module_name`: the darktable IOP module name (e.g., `diffuse`). Must be a key in `KNOWN_MODULES` (see Section 2).

Validation: all three are mandatory. `bench_image` and `bench_sidecar` must point to existing files. `module_name` must be in `KNOWN_MODULES`.

---

## 2. XMP Parsing Module (`optimise/xmp.py`)

New module with a single public function:

```python
def parse_sidecar(xmp_path, module_name):
    """Extract instance labels, params, and pipeline order for a module.

    Returns list of dicts in pipeline execution order:
    [{"label": "bloom", "multi_priority": 0, "params": {"iterations": 10, ...}}, ...]
    """
```

### Steps

1. Parse the XMP file as XML (standard library `xml.etree.ElementTree` with RDF/darktable namespaces).
2. Extract `darktable:iop_order_list` — a comma-separated `name,priority,name,priority,...` string that defines pipeline execution order.
3. Filter `darktable:history` entries where `darktable:operation == module_name` and `darktable:enabled == 1`.
4. For each matching entry, extract `darktable:multi_name`, `darktable:multi_priority`, `darktable:modversion`, and `darktable:params`.
5. Validate `modversion` against `KNOWN_MODULES[module_name]`. Raise an error for unsupported versions.
6. Decode `multi_name` into a clean label. Format is `_builtin_<category> | <name>` (e.g., `_builtin_artistic effects | bloom`) or `_builtin_<name>` with no pipe (e.g., `_builtin_surface blur`). Strip the `_builtin_` prefix; if ` | ` is present, keep only the part after it; otherwise keep everything after `_builtin_`. Empty `multi_name` becomes `"(default)"`.
7. Decode the hex `params` blob using the struct layout for the module version.
8. Sort instances by their position in `iop_order_list` (pipeline execution order).
9. Return the sorted list.

### Known Modules Registry

```python
KNOWN_MODULES = {
    "diffuse": {
        2: {
            "format": "<ififffffffffffi",
            "fields": [
                "iterations", "sharpness", "radius",
                "regularization", "variance_threshold",
                "anisotropy_first", "anisotropy_second",
                "anisotropy_third", "anisotropy_fourth",
                "threshold",
                "first", "second", "third", "fourth",
                "radius_center",
            ],
        },
    },
}
```

The struct format and field names are hardcoded per module version. Only `diffuse` version 2 is supported initially. An unsupported `module_name` or `modversion` raises a clear error at parse time.

### Row ordering

Pipeline execution order is determined by position in `iop_order_list`, filtered to instances that exist in the history. This matches the benchmark output row order (darktable processes instances in pipeline order, bottom-to-top in the UI). Row N in the parser output corresponds to row N in the benchmark output.

---

## 3. `_compute_target()` Changes

Currently stashes `_target_instance_index` and `_target_instance_baseline` in the settings dict. Expanded to also stash:

- `_target_instance_label` — e.g., `"lens deblur | hard"`
- `_target_instance_params` — decoded params dict, e.g., `{"iterations": 10, "radius": 512, ...}`
- `_target_instance_improvement_pct` — how much this instance has improved since baseline
- `_all_instances` — full list from `parse_sidecar()` (labels + params for all instances, in pipeline order)

Calls `parse_sidecar(sidecar_path, module_name)` and cross-references with the result from `find_least_improved_instance()` using the row index.

In `overall` mode, these keys are cleared (popped from settings dict), same as the existing keys.

---

## 4. Prompt Enrichment

Both `build_generation_prompt()` and `build_implementation_prompt()` accept an optional `targeting` dict parameter (default `None`). When present, an "Instance targeting" section is inserted into the prompt.

Example section:

```
# Instance targeting

The benchmark runs 21 instances of the "diffuse" module. Instance 9 ("lens deblur | hard")
has improved the least (+2.1% vs average +8.4%).

Baseline: 9.954s, current best: 9.745s

Parameters for this instance:
  iterations: 10, radius: 512, sharpness: 0.0, radius_center: 0
  1st order speed: -0.25, 2nd order speed: -0.25, 3rd order speed: -0.25, 4th order speed: -0.25
  anisotropy (1st/2nd/3rd/4th): 5.0 / 5.0 / 5.0 / 5.0
  edge sensitivity: 3.0, edge threshold: 0.0, luminance masking: 0.0

Focus your ideas on code paths that would improve performance for these parameters.
```

The `targeting` dict is assembled in `cli.py` from the `_target_*` keys in settings and passed to the prompt builders. In `overall` mode, `targeting` is `None` and the section is omitted.

The generation prompt gets "Focus your ideas on code paths that would improve performance for these parameters." The implementation prompt gets "You are optimizing for this instance. Prioritize code paths exercised by these parameters."

### Formatting params

The params dict is formatted into human-readable grouped lines (not raw key-value dump). Grouping for diffuse:
- Global: iterations, radius, radius_center, sharpness
- Speeds: 1st/2nd/3rd/4th order speed
- Anisotropy: 1st/2nd/3rd/4th order anisotropy
- Masking: edge sensitivity, edge threshold, luminance masking threshold

This formatting is in `xmp.py` as a module-specific function, since field grouping depends on the module.

---

## 5. Benchmark Script Arguments

The optimiser appends `bench_image` and `bench_sidecar` (resolved to absolute paths) as positional arguments to `bench_cmd` wherever it invokes the benchmark:

- `runner.py:run_benchmark_loop()` — accepts `bench_image` and `bench_sidecar` parameters, appends them to the shell command
- `cli.py` baseline step — same

The benchmark script (`bench_diffuse_single.py`) reads `sys.argv[1]` as the image path and `sys.argv[2]` as the sidecar path, replacing its hardcoded `IMAGE` and `XMP` constants.

---

## 6. Change Summary

| Module | Change |
|--------|--------|
| `settings.py` | Add `bench_image`, `bench_sidecar`, `module_name` as mandatory. Validate paths exist, validate `module_name` in `KNOWN_MODULES` |
| `xmp.py` (new) | `parse_sidecar()`, `KNOWN_MODULES` registry, param decoding, label extraction, pipeline ordering, param formatting |
| `cli.py` | `_compute_target()` calls `parse_sidecar()`, stashes label/params. `_generate_ideas()` and implementation step pass targeting dict to prompt builders. Append image/sidecar to bench_cmd |
| `runner.py` | `run_benchmark_loop()` accepts and appends `bench_image`/`bench_sidecar` to `bench_cmd` |
| `prompts.py` | `build_generation_prompt()` and `build_implementation_prompt()` accept optional `targeting` dict, insert "Instance targeting" section |
| `bench_diffuse_single.py` | Read image/sidecar from `sys.argv[1:3]` instead of hardcoded paths |
