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
