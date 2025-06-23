import tempfile
import os
from src.hyprrice.utils import parse_hyprland_config, write_hyprland_config, validate_color

def test_parse_and_write_hyprland_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "hyprland.conf")
        sections = {"general": ["foo=1", "bar=2"]}
        write_hyprland_config(config_path, sections)
        parsed = parse_hyprland_config(config_path)
        assert parsed["general"] == ["foo=1", "bar=2"]

def test_validate_color():
    assert validate_color("#fff")
    assert validate_color("#ffffff")
    assert validate_color("rgb(1,2,3)")
    assert not validate_color("notacolor") 