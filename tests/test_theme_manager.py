import types
from src.hyprrice.gui.theme_manager import ThemeManager

def test_list_themes():
    tm = ThemeManager(themes_dir="/tmp")
    themes = tm.list_themes()
    assert set(themes) == {"minimal", "cyberpunk", "pastel"}

def test_apply_theme():
    tm = ThemeManager(themes_dir="/tmp")
    config = types.SimpleNamespace()
    config.waybar = types.SimpleNamespace()
    config.theme = None
    tm.apply_theme("minimal", config)
    assert config.waybar.background_color == "#222222"
    assert config.theme == "minimal"

def test_preview_theme():
    tm = ThemeManager(themes_dir="/tmp")
    config = types.SimpleNamespace()
    config.theme = None
    tm.preview_theme("cyberpunk", config)
    assert config.theme == "cyberpunk" 