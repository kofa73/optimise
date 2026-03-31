# Prompt Targeting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pass instance-specific context (label, decoded parameters, timing gap) into the generation and implementation LLM prompts so the LLM knows which module instance to focus on.

**Architecture:** Add XMP sidecar parsing (`optimise/xmp.py`), three new mandatory settings (`bench_image`, `bench_sidecar`, `module_name`), enrich `_compute_target()` to stash label/params, and pass a `targeting` dict into both prompt builders. Also update `bench_diffuse_single.py` to accept image/sidecar as CLI arguments, and thread those through `run_benchmark_loop()`.

**Tech Stack:** Python 3.10+, `xml.etree.ElementTree`, `struct`

---

## Task 1: Add `bench_image`, `bench_sidecar`, `module_name` settings

**Files:**
- Modify: `optimise/settings.py`
- Test: `tests/test_settings.py`

- [ ] **Step 1: Write failing tests for the three new settings**

In `tests/test_settings.py`, add to `TestValidateSettings`:

```python
def test_bench_image_validated_as_existing_file(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    img = tmp_path / "test.NEF"
    img.write_text("raw")
    settings["bench_image"] = str(img)
    settings["bench_sidecar"] = str(tmp_path / "test.xmp")
    (tmp_path / "test.xmp").write_text("<xml/>")
    settings["module_name"] = "diffuse"
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["bench_image"] == str(img)

def test_bench_image_missing_file_raises(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    settings["bench_image"] = "nonexistent.NEF"
    settings["bench_sidecar"] = "nonexistent.xmp"
    settings["module_name"] = "diffuse"
    with pytest.raises(SettingsError, match="bench_image"):
        validate_settings(settings, script_repo=str(tmp_path))

def test_bench_sidecar_missing_file_raises(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    img = tmp_path / "test.NEF"
    img.write_text("raw")
    settings["bench_image"] = str(img)
    settings["bench_sidecar"] = "nonexistent.xmp"
    settings["module_name"] = "diffuse"
    with pytest.raises(SettingsError, match="bench_sidecar"):
        validate_settings(settings, script_repo=str(tmp_path))

def test_module_name_validated_against_known_modules(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    img = tmp_path / "test.NEF"
    img.write_text("raw")
    sidecar = tmp_path / "test.xmp"
    sidecar.write_text("<xml/>")
    settings["bench_image"] = str(img)
    settings["bench_sidecar"] = str(sidecar)
    settings["module_name"] = "unknown_module"
    with pytest.raises(SettingsError, match="module_name"):
        validate_settings(settings, script_repo=str(tmp_path))

def test_module_name_diffuse_is_valid(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    img = tmp_path / "test.NEF"
    img.write_text("raw")
    sidecar = tmp_path / "test.xmp"
    sidecar.write_text("<xml/>")
    settings["bench_image"] = str(img)
    settings["bench_sidecar"] = str(sidecar)
    settings["module_name"] = "diffuse"
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["module_name"] == "diffuse"

def test_bench_image_relative_path_resolved(self, tmp_path):
    settings = self._make_valid_settings(tmp_path)
    img = tmp_path / "test.NEF"
    img.write_text("raw")
    sidecar = tmp_path / "test.xmp"
    sidecar.write_text("<xml/>")
    settings["bench_image"] = "test.NEF"
    settings["bench_sidecar"] = "test.xmp"
    settings["module_name"] = "diffuse"
    result = validate_settings(settings, script_repo=str(tmp_path))
    assert result["bench_image"] == str(img)
    assert result["bench_sidecar"] == str(sidecar)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_settings.py -k "bench_image or bench_sidecar or module_name_validated or module_name_diffuse or bench_image_relative" -v`
Expected: FAIL — settings validation doesn't know about these keys yet.

- [ ] **Step 3: Implement validation for the three settings**

In `optimise/settings.py`, add to `_REQUIRED_STRING_KEYS`:

```python
_REQUIRED_STRING_KEYS = ["target_repo", "branch", "optimisation_target", "instructions", "build_cmd", "bench_cmd", "bench_image", "bench_sidecar", "module_name"]
```

In `validate_settings()`, after the `instructions` validation block (around line 106), add:

```python
    # Validate bench_image path
    bench_image = result.get("bench_image", "")
    if bench_image and not os.path.isabs(bench_image):
        bench_image = os.path.join(script_repo, bench_image)
    if not os.path.isfile(bench_image):
        raise SettingsError(f"bench_image file not found: {result['bench_image']}")
    result["bench_image"] = bench_image

    # Validate bench_sidecar path
    bench_sidecar = result.get("bench_sidecar", "")
    if bench_sidecar and not os.path.isabs(bench_sidecar):
        bench_sidecar = os.path.join(script_repo, bench_sidecar)
    if not os.path.isfile(bench_sidecar):
        raise SettingsError(f"bench_sidecar file not found: {result['bench_sidecar']}")
    result["bench_sidecar"] = bench_sidecar

    # Validate module_name against known modules
    from optimise.xmp import KNOWN_MODULES
    module_name = result.get("module_name", "")
    if module_name not in KNOWN_MODULES:
        raise SettingsError(
            f"module_name must be one of {sorted(KNOWN_MODULES.keys())}, "
            f"got: {module_name!r}"
        )
```

- [ ] **Step 4: Add the three settings to SETTINGS_TEMPLATE**

In `optimise/settings.py`, in `SETTINGS_TEMPLATE`, add after the `bench_cmd` line:

```python
# Benchmark input image path, relative to this script repo.
bench_image: <path to benchmark image file>

# XMP sidecar file, relative to this script repo.
# Used to identify module instances and decode their parameters.
bench_sidecar: <path to XMP sidecar file>

# darktable module name to optimise (e.g., diffuse).
module_name: <module name>
```

- [ ] **Step 5: Update _make_valid_settings helper**

The existing test helper `_make_valid_settings` in `tests/test_settings.py` must include the three new mandatory fields so all existing tests keep passing:

```python
def _make_valid_settings(self, tmp_path):
    """Return a minimal valid settings dict."""
    target = tmp_path / "target"
    target.mkdir()
    src = target / "src" / "main.c"
    src.parent.mkdir(parents=True)
    src.write_text("int main() {}")
    instr = tmp_path / "instructions.md"
    instr.write_text("do stuff")
    bench_img = tmp_path / "bench.NEF"
    bench_img.write_text("raw")
    bench_xmp = tmp_path / "bench.xmp"
    bench_xmp.write_text("<xml/>")
    return {
        "target_repo": str(target),
        "branch": "optimise-test",
        "optimisation_target": "src/main.c",
        "instructions": str(instr),
        "build_cmd": "make",
        "bench_cmd": "python bench.py",
        "quality_cmd": "",
        "min_improvement_pct": "0.5",
        "max_regression_pct": "3",
        "early_abort_pct": "10",
        "num_warmup_iterations": "0",
        "benchmark_convergence_threshold_pct": "0.1",
        "benchmark_convergence_tail_runs": "5",
        "max_retries": "5",
        "max_iterations": "50",
        "max_consecutive_perf_failures": "5",
        "max_runtime_minutes": "300",
        "idea_generation_batch_size": "5",
        "commit_prefix": "perf",
        "bench_image": str(bench_img),
        "bench_sidecar": str(bench_xmp),
        "module_name": "diffuse",
    }
```

- [ ] **Step 6: Run all settings tests**

Run: `python3 -m pytest tests/test_settings.py -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add optimise/settings.py tests/test_settings.py
git commit -m "feat: add bench_image, bench_sidecar, module_name settings"
```

---

## Task 2: XMP sidecar parsing — `optimise/xmp.py`

**Files:**
- Create: `optimise/xmp.py`
- Create: `tests/test_xmp.py`

- [ ] **Step 1: Write failing tests for `parse_sidecar`**

Create `tests/test_xmp.py`:

```python
import pytest
import os
from optimise.xmp import parse_sidecar, KNOWN_MODULES, format_params


XMP_PATH = os.path.join(os.path.dirname(__file__), "..", "test-data", "DSC_9034.NEF.xmp")


class TestParseSidecar:
    def test_returns_21_diffuse_instances(self):
        instances = parse_sidecar(XMP_PATH, "diffuse")
        assert len(instances) == 21

    def test_first_instance_is_bloom(self):
        instances = parse_sidecar(XMP_PATH, "diffuse")
        assert instances[0]["label"] == "bloom"
        assert instances[0]["multi_priority"] == 0

    def test_last_instance_is_surface_blur(self):
        instances = parse_sidecar(XMP_PATH, "diffuse")
        assert instances[-1]["label"] == "surface blur"
        assert instances[-1]["multi_priority"] == 22

    def test_bloom_params_decoded(self):
        instances = parse_sidecar(XMP_PATH, "diffuse")
        bloom = instances[0]
        assert bloom["params"]["iterations"] == 10
        assert bloom["params"]["radius"] == 32
        assert bloom["params"]["sharpness"] == pytest.approx(0.0)
        assert bloom["params"]["first"] == pytest.approx(0.5)
        assert bloom["params"]["second"] == pytest.approx(0.5)
        assert bloom["params"]["third"] == pytest.approx(0.5)
        assert bloom["params"]["fourth"] == pytest.approx(0.5)
        assert bloom["params"]["radius_center"] == 0

    def test_pipeline_order_matches_iop_order_list(self):
        """Instances are returned in pipeline execution order."""
        instances = parse_sidecar(XMP_PATH, "diffuse")
        labels = [inst["label"] for inst in instances]
        assert labels[0] == "bloom"
        assert labels[1] == "simulate line drawing"
        assert labels[2] == "simulate watercolor"
        assert labels[-1] == "surface blur"

    def test_unknown_module_raises(self):
        with pytest.raises(ValueError, match="Unknown module"):
            parse_sidecar(XMP_PATH, "nosuchmodule")

    def test_simulate_line_drawing_params(self):
        instances = parse_sidecar(XMP_PATH, "diffuse")
        sld = instances[1]
        assert sld["label"] == "simulate line drawing"
        assert sld["params"]["iterations"] == 11
        assert sld["params"]["radius"] == 64
        assert sld["params"]["first"] == pytest.approx(-1.0)
        assert sld["params"]["second"] == pytest.approx(-1.0)
        assert sld["params"]["third"] == pytest.approx(-1.0)
        assert sld["params"]["fourth"] == pytest.approx(-1.0)


class TestFormatParams:
    def test_formats_diffuse_params(self):
        params = {
            "iterations": 10, "sharpness": 0.0, "radius": 32,
            "regularization": 0.0, "variance_threshold": 0.0,
            "anisotropy_first": 0.0, "anisotropy_second": 0.0,
            "anisotropy_third": 0.0, "anisotropy_fourth": 0.0,
            "threshold": 0.0,
            "first": 0.5, "second": 0.5, "third": 0.5, "fourth": 0.5,
            "radius_center": 0,
        }
        text = format_params("diffuse", params)
        assert "iterations: 10" in text
        assert "radius: 32" in text
        assert "1st order speed: 0.5" in text

    def test_unknown_module_raises(self):
        with pytest.raises(ValueError, match="Unknown module"):
            format_params("nosuchmodule", {})


class TestKnownModules:
    def test_diffuse_version_2_defined(self):
        assert "diffuse" in KNOWN_MODULES
        assert 2 in KNOWN_MODULES["diffuse"]
        info = KNOWN_MODULES["diffuse"][2]
        assert "format" in info
        assert "fields" in info
        assert len(info["fields"]) == 15
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_xmp.py -v`
Expected: FAIL — `optimise/xmp.py` does not exist yet.

- [ ] **Step 3: Implement `optimise/xmp.py`**

Create `optimise/xmp.py`:

```python
"""XMP sidecar parsing for darktable module instance extraction."""
import struct
import xml.etree.ElementTree as ET


DT_NS = "http://darktable.sf.net/"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


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


def _clean_label(multi_name):
    """Convert darktable multi_name to a clean display label.

    Format is '_builtin_<category> | <name>' or '_builtin_<name>'.
    Returns just the descriptive name part, or '(default)' for empty.
    """
    if not multi_name:
        return "(default)"
    name = multi_name
    if name.startswith("_builtin_"):
        name = name[len("_builtin_"):]
    if " | " in name:
        name = name.split(" | ", 1)[1]
    return name


def _decode_params(hex_params, module_name, version):
    """Decode hex-encoded binary params using the struct layout for module+version."""
    if module_name not in KNOWN_MODULES:
        raise ValueError(f"Unknown module: {module_name!r}")
    versions = KNOWN_MODULES[module_name]
    if version not in versions:
        raise ValueError(
            f"Unsupported version {version} for module {module_name!r}. "
            f"Supported: {sorted(versions.keys())}"
        )
    info = versions[version]
    raw = bytes.fromhex(hex_params)
    size = struct.calcsize(info["format"])
    values = struct.unpack(info["format"], raw[:size])
    return dict(zip(info["fields"], values))


def _parse_iop_order(order_str, module_name):
    """Parse iop_order_list and return list of multi_priority values for module_name in pipeline order."""
    items = order_str.split(",")
    priorities = []
    for i in range(0, len(items), 2):
        name = items[i].strip()
        priority = int(items[i + 1].strip())
        if name == module_name:
            priorities.append(priority)
    return priorities


def parse_sidecar(xmp_path, module_name):
    """Extract instance labels, params, and pipeline order for a module.

    Returns list of dicts in pipeline execution order:
    [{"label": "bloom", "multi_priority": 0, "params": {"iterations": 10, ...}}, ...]
    """
    if module_name not in KNOWN_MODULES:
        raise ValueError(f"Unknown module: {module_name!r}")

    tree = ET.parse(xmp_path)
    root = tree.getroot()

    desc = root.find(f".//{{{RDF_NS}}}Description")
    order_str = desc.get(f"{{{DT_NS}}}iop_order_list")
    pipeline_order = _parse_iop_order(order_str, module_name)

    history = desc.find(f"{{{DT_NS}}}history/{{{RDF_NS}}}Seq")
    by_priority = {}
    for item in history.findall(f"{{{RDF_NS}}}li"):
        if item.get(f"{{{DT_NS}}}operation") != module_name:
            continue
        if item.get(f"{{{DT_NS}}}enabled") != "1":
            continue

        priority = int(item.get(f"{{{DT_NS}}}multi_priority"))
        version = int(item.get(f"{{{DT_NS}}}modversion"))
        hex_params = item.get(f"{{{DT_NS}}}params")
        multi_name = item.get(f"{{{DT_NS}}}multi_name", "")

        params = _decode_params(hex_params, module_name, version)
        by_priority[priority] = {
            "label": _clean_label(multi_name),
            "multi_priority": priority,
            "params": params,
        }

    result = []
    for pri in pipeline_order:
        if pri in by_priority:
            result.append(by_priority[pri])

    return result


def format_params(module_name, params):
    """Format decoded params into human-readable grouped text.

    Module-specific grouping for readability in LLM prompts.
    """
    if module_name not in KNOWN_MODULES:
        raise ValueError(f"Unknown module: {module_name!r}")

    if module_name == "diffuse":
        lines = [
            f"  iterations: {params['iterations']}, radius: {params['radius']}, "
            f"radius_center: {params['radius_center']}, sharpness: {params['sharpness']:.1f}",
            f"  1st order speed: {params['first']}, 2nd order speed: {params['second']}, "
            f"3rd order speed: {params['third']}, 4th order speed: {params['fourth']}",
            f"  anisotropy (1st/2nd/3rd/4th): {params['anisotropy_first']} / "
            f"{params['anisotropy_second']} / {params['anisotropy_third']} / "
            f"{params['anisotropy_fourth']}",
            f"  edge sensitivity: {params['regularization']}, "
            f"edge threshold: {params['variance_threshold']}, "
            f"luminance masking: {params['threshold']}",
        ]
        return "\n".join(lines)

    raise ValueError(f"No format_params implementation for module: {module_name!r}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_xmp.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/xmp.py tests/test_xmp.py
git commit -m "feat: add XMP sidecar parsing for module instance extraction"
```

---

## Task 3: Enrich `_compute_target()` with label and params

**Files:**
- Modify: `optimise/cli.py:76-103`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

In `tests/test_cli.py`, update the existing `TestComputeTarget` class. The existing `test_instance_targeting_sets_target_index` test needs updating because `_compute_target` will now also call `parse_sidecar`, so it needs a sidecar file and settings keys. Add new tests:

```python
class TestComputeTarget:
    """_compute_target sets targeting state in settings dict."""

    def _make_sidecar(self, tmp_path):
        """Create a minimal 2-instance XMP sidecar for testing."""
        xmp = tmp_path / "test.xmp"
        xmp.write_text('''\
<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:darktable="http://darktable.sf.net/"
    darktable:iop_order_list="diffuse,0,diffuse,1">
   <darktable:history>
    <rdf:Seq>
     <rdf:li
      darktable:num="0"
      darktable:operation="diffuse"
      darktable:enabled="1"
      darktable:modversion="2"
      darktable:params="0a0000000000000020000000000000000000000000000000000000000000000000000000000000000000003f0000003f0000003f0000003f00000000"
      darktable:multi_name="_builtin_artistic effects | bloom"
      darktable:multi_name_hand_edited="0"
      darktable:multi_priority="0"
      darktable:blendop_version="14"
      darktable:blendop_params=""/>
     <rdf:li
      darktable:num="1"
      darktable:operation="diffuse"
      darktable:enabled="1"
      darktable:modversion="2"
      darktable:params="0b000000000000004000000000008040000000000000a0c00000a0c00000a0c00000a0c000000000000080bf000080bf000080bf000080bf00000000"
      darktable:multi_name="_builtin_lens deblur | hard"
      darktable:multi_name_hand_edited="0"
      darktable:multi_priority="1"
      darktable:blendop_version="14"
      darktable:blendop_params=""/>
    </rdf:Seq>
   </darktable:history>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
''')
        return str(xmp)

    def test_instance_targeting_sets_label_and_params(self, tmp_path):
        """In least_improved_instance mode, stashes label and params."""
        from optimise.benchmark import format_perf_log
        from optimise.cli import _compute_target

        script = tmp_path / "script"
        script.mkdir()
        (script / "perf-logs").mkdir(parents=True)

        baseline = [{"user": 10.0}, {"user": 10.0}]
        current = [{"user": 8.0}, {"user": 9.5}]   # instance 1 least improved
        (script / "perf-logs" / "baseline-perf.md").write_text(format_perf_log(baseline))
        (script / "perf-logs" / "current-best-perf.md").write_text(format_perf_log(current))

        sidecar = self._make_sidecar(tmp_path)
        settings = {
            "targeting_mode": "least_improved_instance",
            "bench_sidecar": sidecar,
            "module_name": "diffuse",
        }

        _compute_target(str(script), settings)

        assert settings["_target_instance_index"] == 1
        assert settings["_target_instance_baseline"] == pytest.approx(10.0)
        assert settings["_target_instance_label"] == "hard"
        assert settings["_target_instance_params"]["iterations"] == 11
        assert settings["_target_instance_improvement_pct"] == pytest.approx(5.0)
        assert settings["_target_instance_current"] == pytest.approx(9.5)
        assert settings["_avg_improvement_pct"] == pytest.approx(12.5)  # (20% + 5%) / 2
        assert len(settings["_all_instances"]) == 2

    def test_overall_mode_clears_all_targeting_state(self, tmp_path):
        """In overall mode, all targeting keys are cleared."""
        from optimise.cli import _compute_target

        settings = {
            "targeting_mode": "overall",
            "_target_instance_index": 1,
            "_target_instance_baseline": 10.0,
            "_target_instance_current": 9.5,
            "_target_instance_label": "bloom",
            "_target_instance_params": {},
            "_target_instance_improvement_pct": 5.0,
            "_avg_improvement_pct": 8.0,
            "_all_instances": [],
        }

        _compute_target(str(tmp_path), settings)

        for key in ("_target_instance_index", "_target_instance_baseline",
                     "_target_instance_current", "_target_instance_label",
                     "_target_instance_params", "_target_instance_improvement_pct",
                     "_avg_improvement_pct", "_all_instances"):
            assert key not in settings
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_cli.py::TestComputeTarget -v`
Expected: FAIL — `_compute_target` doesn't set these new keys.

- [ ] **Step 3: Update `_compute_target()` in `cli.py`**

Replace the `_compute_target` function (lines 76-103):

```python
def _compute_target(directory, settings):
    """Set targeting runtime state in settings dict.

    For 'least_improved_instance' mode, reads baseline and current-best
    perf logs, identifies the least-improved instance, and stashes
    label, params, and timing info from the XMP sidecar.
    For 'overall' mode, clears any previous targeting state.
    """
    target_keys = (
        "_target_instance_index", "_target_instance_baseline",
        "_target_instance_label", "_target_instance_params",
        "_target_instance_improvement_pct", "_all_instances",
    )
    if settings.get("targeting_mode") != "least_improved_instance":
        for key in target_keys:
            settings.pop(key, None)
        return

    baseline_path = os.path.join(directory, "perf-logs", "baseline-perf.md")
    current_path = os.path.join(directory, "perf-logs", "current-best-perf.md")
    with open(baseline_path) as f:
        baseline_rows = parse_perf_log(f.read())
    with open(current_path) as f:
        current_rows = parse_perf_log(f.read())

    target = find_least_improved_instance(baseline_rows, current_rows)

    from optimise.xmp import parse_sidecar
    instances = parse_sidecar(settings["bench_sidecar"], settings["module_name"])

    idx = target["index"]
    settings["_target_instance_index"] = idx
    settings["_target_instance_baseline"] = target["baseline_user"]
    settings["_target_instance_label"] = instances[idx]["label"]
    settings["_target_instance_params"] = instances[idx]["params"]
    settings["_target_instance_improvement_pct"] = target["improvement_pct"]
    settings["_all_instances"] = instances

    log.info(
        f"[TARGET] Instance {idx} (\"{instances[idx]['label']}\"): "
        f"{target['baseline_user']:.3f}s -> {target['current_user']:.3f}s "
        f"({target['improvement_pct']:+.1f}% improvement, least improved)"
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_cli.py::TestComputeTarget -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/cli.py tests/test_cli.py
git commit -m "feat: enrich _compute_target with label, params from XMP sidecar"
```

---

## Task 4: Enrich generation and implementation prompts

**Files:**
- Modify: `optimise/prompts.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: Write failing tests for targeting in generation prompt**

Add to `tests/test_prompts.py`:

```python
class TestGenerationPromptTargeting:
    def _targeting(self):
        return {
            "module_name": "diffuse",
            "instance_count": 21,
            "index": 9,
            "label": "lens deblur | hard",
            "improvement_pct": 2.1,
            "avg_improvement_pct": 8.4,
            "baseline_user": 9.954,
            "current_user": 9.745,
            "params_text": "  iterations: 10, radius: 512",
        }

    def test_includes_targeting_section(self):
        prompt = build_generation_prompt(
            instructions="Optimise",
            learnings="",
            existing_titles=[],
            count=3,
            target_files=["src/diffuse.c"],
            targeting=self._targeting(),
        )
        assert "Instance targeting" in prompt or "instance targeting" in prompt.lower()
        assert "lens deblur | hard" in prompt
        assert "9.954" in prompt
        assert "iterations: 10" in prompt

    def test_no_targeting_section_when_none(self):
        prompt = build_generation_prompt(
            instructions="Optimise",
            learnings="",
            existing_titles=[],
            count=3,
            target_files=["src/diffuse.c"],
            targeting=None,
        )
        assert "Instance targeting" not in prompt

    def test_no_targeting_section_when_omitted(self):
        prompt = build_generation_prompt(
            instructions="Optimise",
            learnings="",
            existing_titles=[],
            count=3,
            target_files=["src/diffuse.c"],
        )
        assert "Instance targeting" not in prompt


class TestImplementationPromptTargeting:
    def _targeting(self):
        return {
            "module_name": "diffuse",
            "instance_count": 21,
            "index": 9,
            "label": "lens deblur | hard",
            "improvement_pct": 2.1,
            "avg_improvement_pct": 8.4,
            "baseline_user": 9.954,
            "current_user": 9.745,
            "params_text": "  iterations: 10, radius: 512",
        }

    def test_includes_targeting_section(self):
        prompt = build_implementation_prompt(
            instructions="Optimise",
            learnings="",
            idea_content="idea",
            target_files=["src/diffuse.c"],
            errors=None,
            targeting=self._targeting(),
        )
        assert "Instance targeting" in prompt or "instance targeting" in prompt.lower()
        assert "lens deblur | hard" in prompt

    def test_no_targeting_section_when_none(self):
        prompt = build_implementation_prompt(
            instructions="Optimise",
            learnings="",
            idea_content="idea",
            target_files=["src/diffuse.c"],
            errors=None,
            targeting=None,
        )
        assert "Instance targeting" not in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_prompts.py -k "Targeting" -v`
Expected: FAIL — functions don't accept `targeting` parameter yet.

- [ ] **Step 3: Implement prompt enrichment**

In `optimise/prompts.py`, update `build_generation_prompt`:

```python
def build_generation_prompt(instructions, learnings, existing_titles, count, target_files,
                            targeting=None):
    """Build prompt for batch idea generation.

    The LLM should read the target files to understand the code, then propose
    `count` optimisation ideas. Each idea needs a filename, title, and description.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)
    existing = "\n".join(f"- {t}" for t in existing_titles) if existing_titles else "(none yet)"

    targeting_section = ""
    if targeting:
        targeting_section = f"""
# Instance targeting

The benchmark runs {targeting['instance_count']} instances of the "{targeting['module_name']}" module. \
Instance {targeting['index']} ("{targeting['label']}") has improved the least \
({targeting['improvement_pct']:+.1f}% vs average {targeting['avg_improvement_pct']:+.1f}%).

Baseline: {targeting['baseline_user']:.3f}s, current best: {targeting['current_user']:.3f}s

Parameters for this instance:
{targeting['params_text']}

Focus your ideas on code paths that would improve performance for these parameters.
"""

    return f"""\
# Instructions

{instructions}

# Target files

Read these files to understand the code: {targets}

# Learnings from past experiments

{learnings}
{targeting_section}
# Existing ideas (do NOT repeat these)

{existing}

# Your task

Generate exactly {count} new optimisation ideas for the target files.

For EACH idea, output in this exact format (with the triple-dash separator between ideas):

---
FILENAME: a-brief-descriptive-name
TITLE: one line suitable as a git commit message
DESCRIPTION:
A short paragraph explaining what to change and why it should improve performance.
---

Rules:
- Filenames must use only [a-zA-Z0-9_-], no extension
- Each idea must be genuinely different from the existing ideas listed above
- Focus on ideas that are likely to succeed based on the learnings
- List ideas in descending order of expected improvement (most impactful first, least impactful last)
"""
```

Update `build_implementation_prompt`:

```python
def build_implementation_prompt(instructions, learnings, idea_content, target_files, errors,
                                targeting=None):
    """Build prompt for implementing an optimisation idea.

    Contains at least three separate, strong prohibitions against running
    builds/tests/benchmarks.
    """
    targets = ", ".join(f"`{t}`" for t in target_files)

    error_block = ""
    if errors:
        error_block = f"""
## PREVIOUS ATTEMPT FAILED

The previous attempt to implement this idea resulted in errors.
You MUST fix these errors. Here is the build/test output:

```
{errors}
```
"""

    targeting_section = ""
    if targeting:
        targeting_section = f"""
# Instance targeting

You are optimising for instance {targeting['index']} ("{targeting['label']}") of the \
"{targeting['module_name']}" module. This instance has improved the least \
({targeting['improvement_pct']:+.1f}% vs average {targeting['avg_improvement_pct']:+.1f}%).

Baseline: {targeting['baseline_user']:.3f}s, current best: {targeting['current_user']:.3f}s

Parameters for this instance:
{targeting['params_text']}

Prioritise code paths exercised by these parameters.
"""

    return f"""\
# Instructions

{instructions}

# Learnings from past experiments

{learnings}
{targeting_section}
# Your task

Implement this optimisation idea by editing the target files ({targets}):

{idea_content}

{error_block}

## CRITICAL RULES — READ EVERY ONE

1. Read the target files and assess whether this idea is still applicable
   given the current state of the code. If the optimisation has already been applied,
   or the code structure has changed making it infeasible, respond with exactly
   `NOT_APPLICABLE` on the first line, followed by a brief explanation. Do nothing else.
2. Use Edit to make ONLY the changes described in the idea. Do not refactor other code.

4. **YOU MUST NOT RUN ANY BUILD COMMANDS. THIS IS FORBIDDEN.**
5. **YOU MUST NOT RUN ANY TEST COMMANDS. THIS IS PROHIBITED.**
6. **YOU MUST NOT RUN ANY BENCHMARK COMMANDS. YOU WILL BE PENALIZED.**
7. **YOU MUST NEVER USE SHELL/BASH TOOLS TO EXECUTE ANYTHING.**
8. **IF YOU ATTEMPT TO BUILD, TEST, OR BENCHMARK, THE SESSION WILL BE TERMINATED.**

The orchestrator script handles ALL building, testing, and benchmarking
after you return control. Your ONLY job is to edit the source files.

When done editing, output a brief summary of what you changed.
"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_prompts.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add optimise/prompts.py tests/test_prompts.py
git commit -m "feat: add instance targeting section to generation and implementation prompts"
```

---

## Task 5: Wire targeting dict from `cli.py` into prompt builders

**Files:**
- Modify: `optimise/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_cli.py`:

```python
class TestTargetingDictAssembly:
    """Verify _build_targeting_dict assembles targeting dict from settings."""

    def test_returns_none_when_no_targeting(self):
        from optimise.cli import _build_targeting_dict
        settings = {"targeting_mode": "overall"}
        assert _build_targeting_dict(settings) is None

    def test_returns_dict_when_targeting(self):
        from optimise.cli import _build_targeting_dict
        settings = {
            "targeting_mode": "least_improved_instance",
            "module_name": "diffuse",
            "_target_instance_index": 9,
            "_target_instance_label": "lens deblur | hard",
            "_target_instance_params": {"iterations": 10, "radius": 512},
            "_target_instance_baseline": 9.954,
            "_target_instance_improvement_pct": 2.1,
            "_all_instances": [{"label": f"inst{i}"} for i in range(21)],
        }
        result = _build_targeting_dict(settings)
        assert result["module_name"] == "diffuse"
        assert result["instance_count"] == 21
        assert result["index"] == 9
        assert result["label"] == "lens deblur | hard"
        assert result["improvement_pct"] == pytest.approx(2.1)
        assert result["baseline_user"] == pytest.approx(9.954)
        assert "params_text" in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_cli.py::TestTargetingDictAssembly -v`
Expected: FAIL — `_build_targeting_dict` does not exist.

- [ ] **Step 3: Add `_build_targeting_dict` and wire into callers**

In `optimise/cli.py`, add after the `_compute_target` function:

```python
def _build_targeting_dict(settings):
    """Assemble targeting dict for prompt builders, or None if not targeting."""
    if settings.get("targeting_mode") != "least_improved_instance":
        return None
    if "_target_instance_label" not in settings:
        return None

    from optimise.xmp import format_params
    from optimise.benchmark import find_least_improved_instance

    instances = settings["_all_instances"]
    idx = settings["_target_instance_index"]

    # Compute average improvement across all instances
    # We don't have per-instance improvements stored, so use the target's improvement
    # and note it's the least. The avg is informational context.
    # Read perf logs to compute average.
    avg_pct = settings.get("_avg_improvement_pct", 0.0)

    return {
        "module_name": settings["module_name"],
        "instance_count": len(instances),
        "index": idx,
        "label": settings["_target_instance_label"],
        "improvement_pct": settings["_target_instance_improvement_pct"],
        "avg_improvement_pct": avg_pct,
        "baseline_user": settings["_target_instance_baseline"],
        "current_user": instances[idx]["params"].get("_current_user",
                        settings["_target_instance_baseline"]),
        "params_text": format_params(settings["module_name"],
                                     settings["_target_instance_params"]),
    }
```

Wait — that `current_user` and `avg_improvement_pct` calculation is awkward. Let me store them properly in `_compute_target`. Update `_compute_target` to also stash `_target_instance_current` and `_avg_improvement_pct`:

In the `_compute_target` function, after computing `target`, add:

```python
    # Compute average improvement for context
    total_improvement = 0.0
    for b_row, c_row in zip(baseline_rows, current_rows):
        total_improvement += (b_row["user"] - c_row["user"]) / b_row["user"] * 100
    avg_improvement = total_improvement / len(baseline_rows)
    settings["_avg_improvement_pct"] = avg_improvement
    settings["_target_instance_current"] = target["current_user"]
```

And add `"_avg_improvement_pct"` and `"_target_instance_current"` to the `target_keys` tuple that gets cleared in overall mode.

Then `_build_targeting_dict` becomes:

```python
def _build_targeting_dict(settings):
    """Assemble targeting dict for prompt builders, or None if not targeting."""
    if settings.get("targeting_mode") != "least_improved_instance":
        return None
    if "_target_instance_label" not in settings:
        return None

    from optimise.xmp import format_params

    return {
        "module_name": settings["module_name"],
        "instance_count": len(settings["_all_instances"]),
        "index": settings["_target_instance_index"],
        "label": settings["_target_instance_label"],
        "improvement_pct": settings["_target_instance_improvement_pct"],
        "avg_improvement_pct": settings["_avg_improvement_pct"],
        "baseline_user": settings["_target_instance_baseline"],
        "current_user": settings["_target_instance_current"],
        "params_text": format_params(settings["module_name"],
                                     settings["_target_instance_params"]),
    }
```

Update `_generate_ideas` to pass targeting:

```python
def _generate_ideas(directory, settings, ai, target_repo_path, instructions, target_files):
    needed = settings["idea_generation_batch_size"]
    if needed <= 0:
        return GenerationResult.OK

    learnings = _read_learnings(directory)
    existing_titles = all_idea_titles(directory)
    targeting = _build_targeting_dict(settings)

    prompt = build_generation_prompt(
        instructions, learnings, existing_titles, needed, target_files,
        targeting=targeting,
    )
    output, rc, provider = ai.call(
        prompt, tier="best", cwd=target_repo_path,
        timeout=settings["llm_timeout"], purpose="generating ideas",
    )
    if rc != 0:
        log.warning(f"Idea generation failed ({provider})")
        return GenerationResult.LLM_FAILURE

    ideas = parse_generated_ideas(output)
    if not ideas:
        return GenerationResult.LLM_FAILURE

    for idx, idea in enumerate(ideas, start=1):
        content = f"{idea['title']}\n\n{idea['description']}"
        create_idea(directory, idea["filename"], content, ordinal=idx)

    return GenerationResult.OK
```

Update the CODE state block to pass targeting to `build_implementation_prompt`:

```python
            targeting = _build_targeting_dict(settings)
            prompt = build_implementation_prompt(
                instructions, learnings, idea_content, target_files, errors,
                targeting=targeting,
            )
```

- [ ] **Step 4: Update the test for _build_targeting_dict**

Update the test to match the final signature, adding `_avg_improvement_pct` and `_target_instance_current` to settings:

```python
    def test_returns_dict_when_targeting(self):
        from optimise.cli import _build_targeting_dict
        settings = {
            "targeting_mode": "least_improved_instance",
            "module_name": "diffuse",
            "_target_instance_index": 9,
            "_target_instance_label": "lens deblur | hard",
            "_target_instance_params": {
                "iterations": 10, "sharpness": 0.0, "radius": 512,
                "regularization": 3.0, "variance_threshold": 0.0,
                "anisotropy_first": 5.0, "anisotropy_second": 5.0,
                "anisotropy_third": 5.0, "anisotropy_fourth": 5.0,
                "threshold": 0.0,
                "first": -0.25, "second": -0.25, "third": -0.25, "fourth": -0.25,
                "radius_center": 0,
            },
            "_target_instance_baseline": 9.954,
            "_target_instance_current": 9.745,
            "_target_instance_improvement_pct": 2.1,
            "_avg_improvement_pct": 8.4,
            "_all_instances": [{"label": f"inst{i}"} for i in range(21)],
        }
        result = _build_targeting_dict(settings)
        assert result["module_name"] == "diffuse"
        assert result["instance_count"] == 21
        assert result["index"] == 9
        assert result["label"] == "lens deblur | hard"
        assert result["improvement_pct"] == pytest.approx(2.1)
        assert result["avg_improvement_pct"] == pytest.approx(8.4)
        assert result["baseline_user"] == pytest.approx(9.954)
        assert result["current_user"] == pytest.approx(9.745)
        assert "iterations: 10" in result["params_text"]
```

- [ ] **Step 5: Run tests**

Run: `python3 -m pytest tests/test_cli.py::TestTargetingDictAssembly tests/test_cli.py::TestComputeTarget -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add optimise/cli.py tests/test_cli.py
git commit -m "feat: wire targeting dict into generation and implementation prompts"
```

---

## Task 6: Pass bench_image and bench_sidecar to benchmark script

**Files:**
- Modify: `optimise/runner.py:128-192`
- Modify: `optimise/cli.py` (baseline step, benchmark calls)
- Modify: `bench_diffuse_single.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for run_benchmark_loop accepting image/sidecar**

In `tests/test_cli.py`, find or add a test that verifies bench_cmd includes image/sidecar args. Since `run_benchmark_loop` calls `subprocess.run` directly, we test via the call args:

```python
class TestBenchmarkArgsPassthrough:
    """bench_image and bench_sidecar are appended to bench_cmd."""

    def test_run_benchmark_loop_appends_args(self):
        from unittest.mock import patch, MagicMock
        from optimise.runner import run_benchmark_loop

        mock_result = MagicMock()
        mock_result.stdout = "user=1.0, cpu=2.0\n"
        mock_result.returncode = 0

        with patch("optimise.runner.subprocess.run", return_value=mock_result) as mock_run:
            run_benchmark_loop(
                bench_cmd="python bench.py",
                cwd="/tmp",
                baseline_user_sum=float("inf"),
                num_warmup=0,
                convergence_threshold_pct=100,  # converge immediately
                convergence_tail_runs=1,
                early_abort_pct=0,
                bench_image="/path/to/image.NEF",
                bench_sidecar="/path/to/image.xmp",
            )
        # Check the command includes the image and sidecar
        cmd = mock_run.call_args_list[-1][0][0]
        assert "/path/to/image.NEF" in cmd
        assert "/path/to/image.xmp" in cmd
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_cli.py::TestBenchmarkArgsPassthrough -v`
Expected: FAIL — `run_benchmark_loop` doesn't accept `bench_image`/`bench_sidecar`.

- [ ] **Step 3: Update `run_benchmark_loop` in `runner.py`**

Add `bench_image=None` and `bench_sidecar=None` parameters:

```python
def run_benchmark_loop(bench_cmd, cwd, baseline_user_sum,
                       num_warmup, convergence_threshold_pct,
                       convergence_tail_runs, early_abort_pct,
                       target_instance_index=None,
                       target_instance_baseline=None,
                       bench_image=None, bench_sidecar=None):
    """Run the benchmark convergence loop.

    Returns element-wise best rows on success.
    Raises BenchmarkError on early abort or parse failure.
    """
    # Build the full command with optional image/sidecar args
    full_cmd = bench_cmd
    if bench_image and bench_sidecar:
        full_cmd = f"{bench_cmd} {bench_image} {bench_sidecar}"

    # Warmup
    for i in range(num_warmup):
        log.info(f"BENCH warmup {i+1}/{num_warmup}")
        subprocess.run(
            full_cmd, shell=True,
            capture_output=True, text=True, cwd=cwd,
        )

    best = None
    convergence = ConvergenceState(convergence_threshold_pct, convergence_tail_runs)
    run_idx = 0

    while True:
        run_idx += 1
        log.info(f"BENCH run {run_idx}")

        result = subprocess.run(
            full_cmd, shell=True,
            capture_output=True, text=True, cwd=cwd,
        )
        rows = parse_bench_output(result.stdout)
        best = update_element_best(best, rows)
        current_sum = sum_user(best)

        # Early abort on first real run
        if run_idx == 1:
            sum_threshold = baseline_user_sum * (1 - early_abort_pct / 100)
            sum_exceeded = current_sum > sum_threshold

            instance_exceeded = False
            if target_instance_index is not None and target_instance_baseline is not None:
                instance_time = best[target_instance_index]["user"]
                instance_threshold = target_instance_baseline * (1 - early_abort_pct / 100)
                instance_exceeded = instance_time > instance_threshold

            if sum_exceeded or instance_exceeded:
                improvement_pct = (1 - current_sum / baseline_user_sum) * 100
                raise BenchmarkError(
                    f"Benchmark early abort: {current_sum:.3f}s vs "
                    f"baseline {baseline_user_sum:.3f}s "
                    f"({improvement_pct:+.1f}%, need {early_abort_pct}%)",
                    rows=best,
                )

        convergence.update(current_sum)
        log.info(f"BENCH run {run_idx}: sum(user)={current_sum:.3f}s "
                 f"(tail={convergence.tail_counter}/{convergence_tail_runs})")

        if convergence.converged:
            log.info(f"BENCH converged after {run_idx} runs")
            break

    return best
```

- [ ] **Step 4: Update all `run_benchmark_loop` call sites in `cli.py`**

In `cli.py`, update the BASELINE benchmark call (around line 237):

```python
            try:
                best = run_benchmark_loop(
                    settings["bench_cmd"], cwd=target_repo_path,
                    baseline_user_sum=float("inf"),
                    num_warmup=settings["num_warmup_iterations"],
                    convergence_threshold_pct=settings["benchmark_convergence_threshold_pct"],
                    convergence_tail_runs=settings["benchmark_convergence_tail_runs"],
                    early_abort_pct=settings["early_abort_pct"],
                    bench_image=settings["bench_image"],
                    bench_sidecar=settings["bench_sidecar"],
                )
```

In `_do_build_test_benchmark` (around line 512):

```python
        best = run_benchmark_loop(
            s.settings["bench_cmd"], cwd=s.target_repo_path,
            baseline_user_sum=baseline_sum,
            num_warmup=s.settings["num_warmup_iterations"],
            convergence_threshold_pct=s.settings["benchmark_convergence_threshold_pct"],
            convergence_tail_runs=s.settings["benchmark_convergence_tail_runs"],
            early_abort_pct=s.settings["early_abort_pct"],
            target_instance_index=s.settings.get("_target_instance_index"),
            target_instance_baseline=s.settings.get("_target_instance_baseline"),
            bench_image=s.settings["bench_image"],
            bench_sidecar=s.settings["bench_sidecar"],
        )
```

In `do_command` benchmark section (around line 731):

```python
            best = run_benchmark_loop(
                settings["bench_cmd"], cwd=target_repo_path,
                baseline_user_sum=float("inf"),
                num_warmup=settings["num_warmup_iterations"],
                convergence_threshold_pct=settings["benchmark_convergence_threshold_pct"],
                convergence_tail_runs=settings["benchmark_convergence_tail_runs"],
                early_abort_pct=settings["early_abort_pct"],
                bench_image=settings["bench_image"],
                bench_sidecar=settings["bench_sidecar"],
            )
```

- [ ] **Step 5: Update `bench_diffuse_single.py`**

Replace the hardcoded paths:

```python
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
```

- [ ] **Step 6: Run tests**

Run: `python3 -m pytest tests/test_cli.py::TestBenchmarkArgsPassthrough -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add optimise/runner.py optimise/cli.py bench_diffuse_single.py tests/test_cli.py
git commit -m "feat: pass bench_image and bench_sidecar to benchmark script"
```

---

## Task 7: Update settings.conf and CLAUDE.md

**Files:**
- Modify: `settings.conf`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add the three new settings to settings.conf**

Add after the `bench_cmd` line in `settings.conf`:

```
bench_image: test-data/DSC_9034.NEF
bench_sidecar: test-data/DSC_9034.NEF.xmp
module_name: diffuse
```

- [ ] **Step 2: Update CLAUDE.md module table**

Add `xmp.py` to the Module Responsibilities table:

```
| `xmp.py` | Parse XMP sidecar files — extract module instance labels, params, pipeline order |
```

- [ ] **Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add settings.conf CLAUDE.md
git commit -m "docs: add bench_image, bench_sidecar, module_name to settings.conf and CLAUDE.md"
```
