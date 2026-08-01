"""Core logic for building KDE Plasma desktop entries, Konsole layouts, and Desktop Actions."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from .config import LauncherConfig


class DesktopEntryGenerator:
    """Generator for Freedesktop / KDE Plasma 6 .desktop entries, Desktop Actions, and Konsole layouts."""

    @staticmethod
    def generate_split_layout(config: LauncherConfig) -> str:
        """Generate a valid Konsole layout JSON structure representing a 2x2 grid (4 panes).

        Configures each split pane to execute the target AI binary command upon creation.
        Target file location: ~/.config/konsole/<model_id>-4split.json
        """
        pane = {"Command": config.binary_command}
        layout_dict: Dict[str, Any] = {
            "Orientation": "Vertical",
            "Widgets": [
                {
                    "Orientation": "Horizontal",
                    "Widgets": [pane, pane],
                },
                {
                    "Orientation": "Horizontal",
                    "Widgets": [pane, pane],
                },
            ],
        }
        return json.dumps(layout_dict, indent=2) + "\n"

    @staticmethod
    def generate_tab_layout(config: LauncherConfig) -> str:
        """Generate a Konsole --tabs-from-file format file containing 4 tab definitions.

        Titles each tab (e.g. 'Session 1', 'Session 2', etc.) and sets each to execute the model binary command.
        Target file location: ~/.config/konsole/<model_id>-4tabs.tabs
        """
        lines = [
            f"title: Session {i} ;; command: {config.binary_command}"
            for i in range(1, 5)
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_desktop_entry(
        config: LauncherConfig,
        konsole_dir: Optional[Path] = None,
    ) -> str:
        """Build a complete Freedesktop .desktop specification with KDE Desktop Actions (Split4 and Tabs4).

        Args:
            config: LauncherConfig instance.
            konsole_dir: Target Konsole configuration directory. Defaults to ~/.config/konsole with expanded $HOME.
        """
        if konsole_dir is None:
            konsole_dir = Path.home() / ".config/konsole"
        else:
            konsole_dir = konsole_dir.expanduser()

        split_json_path = konsole_dir / f"{config.model_id}-4split.json"
        tabs_file_path = konsole_dir / f"{config.model_id}-4tabs.tabs"

        categories_str = ";".join(config.categories)
        if categories_str and not categories_str.endswith(";"):
            categories_str += ";"

        terminal_str = "true" if config.terminal else "false"

        # Main launch command: konsole -e <binary_command>
        exec_cmd = f"konsole -e {config.binary_command}" if not config.binary_command.startswith("konsole ") else config.binary_command

        lines = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={config.model_name}",
            f"Comment={config.comment}",
            f"Exec={exec_cmd}",
            f"Icon={config.icon}",
            f"Terminal={terminal_str}",
            f"Categories={categories_str}",
            "Keywords=AI;LLM;CLI;KDE;Terminal;Claude;Antigravity;Codex;Konsole;Grid;Tabs;",
            "StartupNotify=true",
            "X-KDE-SubstituteUID=false",
            "Actions=Split4;Tabs4;",
            "",
            "[Desktop Action Split4]",
            "Name=Launch 4-Pane Split Grid",
            f"Exec=konsole --layout {split_json_path}",
            "Icon=view-grid",
            "",
            "[Desktop Action Tabs4]",
            "Name=Launch 4-Tab Session",
            f"Exec=konsole --tabs-from-file {tabs_file_path}",
            "Icon=tab-duplicate",
        ]

        if config.konsole_profile:
            lines.insert(11, f"X-KDE-KonsoleProfile={config.konsole_profile}")

        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_konsole_profile(config: LauncherConfig) -> str:
        """Build a custom KDE Konsole profile file content targeting Konsole on KDE Plasma 6."""
        lines = [
            "[General]",
            f"Name={config.model_name}",
            "Parent=FALLBACK/",
            "",
            "[Command]",
            f"CommandLine={config.binary_command}",
            "",
            "[Appearance]",
            "ColorScheme=BreezeDark",
        ]
        return "\n".join(lines) + "\n"
