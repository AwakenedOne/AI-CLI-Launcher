"""Tests for LauncherConfig and DesktopEntryGenerator layout and action generators."""

import json
from pathlib import Path
from kde_ai_launcher.config import LauncherConfig
from kde_ai_launcher.generator import DesktopEntryGenerator


def test_launcher_config_defaults():
    config = LauncherConfig(model_name="Claude", binary_command="claude")
    assert config.desktop_filename == "ai-claude.desktop"
    assert config.model_id == "claude"
    assert config.wm_class == "ai-claude"
    assert config.icon == "utilities-terminal"


def test_target_models_config():
    models = [
        ("Claude", "claude", "ai-claude.desktop", "ai-claude"),
        ("Antigravity", "antigravity", "ai-antigravity.desktop", "ai-antigravity"),
        ("Codex", "codex", "ai-codex.desktop", "ai-codex"),
    ]
    for name, cmd, expected_file, expected_wmclass in models:
        cfg = LauncherConfig(model_name=name, binary_command=cmd)
        assert cfg.model_name == name
        assert cfg.binary_command == cmd
        assert cfg.desktop_filename == expected_file
        assert cfg.wm_class == expected_wmclass


def test_split_layout_generation():
    config = LauncherConfig(model_name="Claude", binary_command="claude")
    split_json = DesktopEntryGenerator.generate_split_layout(config)
    data = json.loads(split_json)

    assert data["Orientation"] == "Vertical"
    assert len(data["Widgets"]) == 2
    for row in data["Widgets"]:
        assert row["Orientation"] == "Horizontal"
        assert len(row["Widgets"]) == 2
        for pane in row["Widgets"]:
            assert pane["Command"] == "claude"


def test_tab_layout_generation():
    config = LauncherConfig(model_name="Antigravity", binary_command="antigravity")
    tab_content = DesktopEntryGenerator.generate_tab_layout(config)
    lines = [line for line in tab_content.strip().split("\n") if line]

    assert len(lines) == 4
    assert "title: Session 1 ;; command: antigravity" in lines[0]
    assert "title: Session 4 ;; command: antigravity" in lines[3]


def test_desktop_entry_with_actions_and_wmclass():
    config = LauncherConfig(
        model_name="Codex",
        binary_command="codex",
        icon="codex.svg",
        desktop_filename="ai-codex.desktop",
    )
    konsole_dir = Path("/home/user/.config/konsole")
    content = DesktopEntryGenerator.generate_desktop_entry(config, konsole_dir=konsole_dir)

    assert "[Desktop Entry]" in content
    assert "Name=Codex" in content
    assert "Exec=konsole --class ai-codex -e codex" in content
    assert "Icon=" in content
    assert "codex.svg" in content
    assert "Terminal=false" in content
    assert "StartupWMClass=ai-codex" in content
    assert "Actions=Split4;Tabs4;" in content

    # Check Desktop Actions with --class parameter
    assert "[Desktop Action Split4]" in content
    assert "Exec=konsole --class ai-codex --layout /home/user/.config/konsole/codex-4split.json" in content
    assert "[Desktop Action Tabs4]" in content
    assert "Exec=konsole --class ai-codex --tabs-from-file /home/user/.config/konsole/codex-4tabs.tabs" in content
