import os
import pytest
from src.hyprrice.config import Config
from src.hyprrice.utils import backup_file, restore_file

def test_config_load_save(tmp_path):
    config_path = tmp_path / "config.yaml"
    config = Config()
    config.general.language = "fr"
    config.save(str(config_path))
    loaded = Config.load(str(config_path))
    assert loaded.general.language == "fr"

def test_config_validation():
    config = Config()
    assert config.validate() is True
    config.hyprland.window_opacity = 2.0
    with pytest.raises(Exception):
        config.validate()

def test_backup_restore(tmp_path):
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        f.write("test: 1\n")
    backup_dir = tmp_path / "backups"
    backup_path = backup_file(str(config_path), str(backup_dir))
    # Overwrite file
    with open(config_path, "w") as f:
        f.write("test: 2\n")
    restore_file(backup_path, str(config_path))
    with open(config_path) as f:
        assert "test: 1" in f.read() 