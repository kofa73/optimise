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
    """Parse iop_order_list and return multi_priority values for module_name in pipeline order."""
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
    """Format decoded params into human-readable grouped text for LLM prompts."""
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
