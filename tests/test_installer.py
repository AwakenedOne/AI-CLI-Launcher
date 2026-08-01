"""Tests for LauncherInstaller."""

import json
from pathlib import Path
import tempfile
from kde_ai_launcher.config import LauncherConfig
from kde_ai_launcher.installer import LauncherInstaller


def test_installer_file_creation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        apps_dir = tmp_path / "applications"
        konsole_dir = tmp_path / "konsole"
        icons_dir = tmp_path / "icons"

        installer = LauncherInstaller(apps_dir=apps_dir, konsole_dir=konsole_dir, icons_dir=icons_dir)

        config = LauncherConfig(
            model_name="Test LLM",
            binary_command="python3 --version",
            desktop_filename="ai-test-llm.desktop",
        )

        installed_files = installer.install(config, install_konsole_profile=True)

        assert "desktop" in installed_files
        assert installed_files["desktop"].exists()
        assert installed_files["desktop"].name == "ai-test-llm.desktop"

        assert "split_layout" in installed_files
        assert installed_files["split_layout"].exists()
        assert installed_files["split_layout"].name == "test-llm-4split.json"
        layout_json = json.loads(installed_files["split_layout"].read_text(encoding="utf-8"))
        assert layout_json["Orientation"] == "Vertical"

        assert "tab_layout" in installed_files
        assert installed_files["tab_layout"].exists()
        assert installed_files["tab_layout"].name == "test-llm-4tabs.tabs"
        tabs_text = installed_files["tab_layout"].read_text(encoding="utf-8")
        assert "Session 1" in tabs_text

        assert "profile" in installed_files
        assert installed_files["profile"].exists()


def test_installer_binary_check():
    installer = LauncherInstaller()
    assert installer.check_binary_exists("python3") is True
    assert installer.check_binary_exists("nonexistent_binary_xyz_123") is False
