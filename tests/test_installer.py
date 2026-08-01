"""Tests for LauncherInstaller."""

import json
import os
import stat
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

        # Create dummy icon file
        custom_icon = tmp_path / "custom.svg"
        custom_icon.write_text("<svg></svg>", encoding="utf-8")

        installer = LauncherInstaller(apps_dir=apps_dir, konsole_dir=konsole_dir, icons_dir=icons_dir)

        config = LauncherConfig(
            model_name="Test LLM",
            binary_command="python3 --version",
            icon=str(custom_icon),
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

        assert "icon" in installed_files
        assert installed_files["icon"].exists()
        mode = installed_files["icon"].stat().st_mode
        assert stat.S_IMODE(mode) == 0o644

        # Desktop file should use absolute icon path
        desktop_content = installed_files["desktop"].read_text(encoding="utf-8")
        assert f"Icon={installed_files['icon'].resolve()}" in desktop_content


def test_installer_binary_check():
    installer = LauncherInstaller()
    assert installer.check_binary_exists("python3") is True
    assert installer.check_binary_exists("nonexistent_binary_xyz_123") is False
