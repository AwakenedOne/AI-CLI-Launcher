"""Tests for CLI entry point and zero-config / advanced modes."""

from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock

from kde_ai_launcher.cli import (
    get_default_configs,
    get_default_icon_for_model,
    main,
)
from kde_ai_launcher.config import LauncherConfig
from kde_ai_launcher.installer import LauncherInstaller


def test_get_default_configs():
    configs = get_default_configs()
    assert len(configs) == 3

    claude = configs[0]
    assert claude.model_name == "Claude"
    assert claude.binary_command == "claude"
    assert claude.desktop_filename == "ai-claude.desktop"
    assert "ai-claude.svg" in claude.icon

    antigravity = configs[1]
    assert antigravity.model_name == "Antigravity"
    assert antigravity.binary_command == "agy"
    assert antigravity.desktop_filename == "ai-antigravity.desktop"
    assert "ai-antigravity.svg" in antigravity.icon

    codex = configs[2]
    assert codex.model_name == "Codex"
    assert codex.binary_command == "codex"
    assert codex.desktop_filename == "ai-codex.desktop"
    assert "ai-codex.svg" in codex.icon


def test_get_default_icon_for_model():
    assert "ai-claude.svg" in get_default_icon_for_model("claude")
    assert "ai-antigravity.svg" in get_default_icon_for_model("antigravity")
    assert "ai-codex.svg" in get_default_icon_for_model("codex")
    assert get_default_icon_for_model("unknown_model_xyz") == "utilities-terminal"


def test_cli_generate_zero_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        apps_dir = tmp_path / "applications"

        with patch("kde_ai_launcher.cli.LauncherInstaller") as MockInstaller:
            mock_inst = MagicMock()
            mock_inst.install.return_value = {"desktop": apps_dir / "test.desktop"}
            mock_inst.refresh_kde_cache.return_value = ["Cache refreshed"]
            MockInstaller.return_value = mock_inst

            exit_code = main(["generate"])
            assert exit_code == 0
            assert mock_inst.install.call_count == 3


def test_cli_install_zero_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        apps_dir = tmp_path / "applications"

        with patch("kde_ai_launcher.cli.LauncherInstaller") as MockInstaller:
            mock_inst = MagicMock()
            mock_inst.install.return_value = {"desktop": apps_dir / "test.desktop"}
            mock_inst.refresh_kde_cache.return_value = ["Cache refreshed"]
            MockInstaller.return_value = mock_inst

            exit_code = main(["install"])
            assert exit_code == 0
            assert mock_inst.install.call_count == 3


def test_installer_bundled_icon_copy():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        apps_dir = tmp_path / "applications"
        konsole_dir = tmp_path / "konsole"
        icons_dir = tmp_path / "icons"

        installer = LauncherInstaller(apps_dir=apps_dir, konsole_dir=konsole_dir, icons_dir=icons_dir)

        config = LauncherConfig(
            model_name="Claude",
            binary_command="claude",
            icon="ai-claude.svg",
            desktop_filename="ai-claude.desktop",
        )

        installed = installer.install(config)
        assert "icon" in installed
        assert installed["icon"].exists()
        assert installed["icon"].name == "ai-claude.svg"
        assert config.icon == str(installed["icon"])


def test_installer_uninstall():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        apps_dir = tmp_path / "applications"
        konsole_dir = tmp_path / "konsole"
        icons_dir = tmp_path / "icons"

        installer = LauncherInstaller(apps_dir=apps_dir, konsole_dir=konsole_dir, icons_dir=icons_dir)

        config = LauncherConfig(
            model_name="Claude",
            binary_command="claude",
            icon="ai-claude.svg",
            desktop_filename="ai-claude.desktop",
        )

        installer.install(config)
        assert (apps_dir / "ai-claude.desktop").exists()
        assert (konsole_dir / "claude-4split.json").exists()
        assert (konsole_dir / "claude-4tabs.tabs").exists()

        removed = installer.uninstall([config])
        assert len(removed) >= 3
        assert not (apps_dir / "ai-claude.desktop").exists()
        assert not (konsole_dir / "claude-4split.json").exists()
        assert not (konsole_dir / "claude-4tabs.tabs").exists()


def test_cli_uninstall_command():
    with patch("kde_ai_launcher.cli.LauncherInstaller") as MockInstaller:
        mock_inst = MagicMock()
        mock_inst.uninstall.return_value = [Path("/tmp/test.desktop")]
        mock_inst.refresh_kde_cache.return_value = ["Cache refreshed"]
        MockInstaller.return_value = mock_inst

        exit_code = main(["uninstall", "--yes"])
        assert exit_code == 0
        assert mock_inst.uninstall.call_count == 1
