"""File installer and KDE desktop database refresh handler."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from .config import LauncherConfig
from .generator import DesktopEntryGenerator

ASSETS_ICONS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"
if not ASSETS_ICONS_DIR.exists():
    ASSETS_ICONS_DIR = Path(__file__).resolve().parent / "assets" / "icons"


class LauncherInstaller:
    """Installer responsible for writing launcher assets, layout files, and updating KDE system caches."""

    DEFAULT_APPS_DIR = Path.home() / ".local/share/applications"
    DEFAULT_KONSOLE_DIR = Path.home() / ".config/konsole"
    DEFAULT_ICONS_DIR = Path.home() / ".local/share/icons"

    def __init__(
        self,
        apps_dir: Optional[Path] = None,
        konsole_dir: Optional[Path] = None,
        icons_dir: Optional[Path] = None,
    ):
        self.apps_dir = (apps_dir or self.DEFAULT_APPS_DIR).expanduser()
        self.konsole_dir = (konsole_dir or self.DEFAULT_KONSOLE_DIR).expanduser()
        self.icons_dir = (icons_dir or self.DEFAULT_ICONS_DIR).expanduser()

    def copy_bundled_icons(self) -> List[Path]:
        """Copy all bundled SVG icon files from assets/icons/ to the system icon directory with 644 permissions."""
        copied: List[Path] = []
        if not ASSETS_ICONS_DIR.exists() or not list(ASSETS_ICONS_DIR.glob("*.svg")):
            print(f"[!] Warning: Bundled icon directory '{ASSETS_ICONS_DIR}' or SVG assets missing.", file=sys.stderr)
            return copied

        try:
            self.icons_dir.mkdir(parents=True, exist_ok=True)
            for svg_file in ASSETS_ICONS_DIR.glob("*.svg"):
                target_path = self.icons_dir / svg_file.name
                shutil.copy2(svg_file, target_path)
                os.chmod(target_path, 0o644)
                copied.append(target_path)
        except OSError as e:
            print(f"[!] Warning: Failed to copy bundled icons: {e}", file=sys.stderr)

        return copied

    def uninstall(self, configs: Optional[List[LauncherConfig]] = None) -> List[Path]:
        """Safely remove all installed desktop entries, Konsole layout files, and model icons."""
        removed_files: List[Path] = []

        target_desktop_files = {"ai-claude.desktop", "ai-antigravity.desktop", "ai-codex.desktop", "ai-launcher.desktop"}
        target_icon_files = {"claude.svg", "antigravity.svg", "codex.svg", "ai-launcher.svg"}
        target_model_ids = {"claude", "antigravity", "codex"}

        if configs:
            for cfg in configs:
                target_desktop_files.add(cfg.desktop_filename)
                target_model_ids.add(cfg.model_id)

        # 1. Remove desktop entries
        if self.apps_dir.exists():
            for desktop_name in target_desktop_files:
                desktop_path = self.apps_dir / desktop_name
                if desktop_path.exists():
                    try:
                        desktop_path.unlink()
                        removed_files.append(desktop_path)
                    except OSError as e:
                        print(f"[!] Warning: Could not delete '{desktop_path}': {e}", file=sys.stderr)

            for desktop_path in self.apps_dir.glob("ai-*.desktop"):
                if desktop_path.exists() and desktop_path not in removed_files:
                    try:
                        content = desktop_path.read_text(encoding="utf-8", errors="ignore")
                        if "Actions=Split4;Tabs4;" in content or "KDE AI Launcher" in content:
                            desktop_path.unlink()
                            removed_files.append(desktop_path)
                    except OSError:
                        pass

        # 2. Remove Konsole layout files
        if self.konsole_dir.exists():
            for model_id in target_model_ids:
                split_file = self.konsole_dir / f"{model_id}-4split.json"
                tabs_file = self.konsole_dir / f"{model_id}-4tabs.tabs"
                for target_file in (split_file, tabs_file):
                    if target_file.exists() and target_file not in removed_files:
                        try:
                            target_file.unlink()
                            removed_files.append(target_file)
                        except OSError as e:
                            print(f"[!] Warning: Could not delete '{target_file}': {e}", file=sys.stderr)

            for split_file in self.konsole_dir.glob("*-4split.json"):
                if split_file not in removed_files:
                    try:
                        split_file.unlink()
                        removed_files.append(split_file)
                    except OSError:
                        pass
            for tabs_file in self.konsole_dir.glob("*-4tabs.tabs"):
                if tabs_file not in removed_files:
                    try:
                        tabs_file.unlink()
                        removed_files.append(tabs_file)
                    except OSError:
                        pass

        # 3. Remove icon files
        if self.icons_dir.exists():
            for icon_name in target_icon_files:
                icon_path = self.icons_dir / icon_name
                if icon_path.exists() and icon_path not in removed_files:
                    try:
                        icon_path.unlink()
                        removed_files.append(icon_path)
                    except OSError as e:
                        print(f"[!] Warning: Could not delete '{icon_path}': {e}", file=sys.stderr)

        return removed_files

    def check_binary_exists(self, binary_command: str) -> bool:
        """Check if the primary binary command executable exists in system PATH."""
        if not binary_command:
            return False
        first_word = binary_command.split()[0]
        return shutil.which(first_word) is not None

    def install(
        self,
        config: LauncherConfig,
        install_konsole_profile: bool = False,
    ) -> Dict[str, Path]:
        """Write the .desktop entry, split grid layout, tab layout, and optional Konsole profile to disk safely.

        Returns:
            Dict[str, Path]: Mapping of file types ('desktop', 'split_layout', 'tab_layout', 'profile', 'icon') to installed file paths.
        """
        # 0. Check binary warning
        if not self.check_binary_exists(config.binary_command):
            first_word = config.binary_command.split()[0] if config.binary_command else ""
            print(f"[!] Warning: Command '{first_word}' was not found in system PATH. File creation will continue.", file=sys.stderr)

        installed_files: Dict[str, Path] = {}

        try:
            self.apps_dir.mkdir(parents=True, exist_ok=True)
            self.konsole_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"[-] Error creating installation directories: {e}", file=sys.stderr)
            raise

        try:
            # 1. Generate & write Konsole 4-split grid layout JSON
            split_path = self.konsole_dir / f"{config.model_id}-4split.json"
            split_content = DesktopEntryGenerator.generate_split_layout(config)
            split_path.write_text(split_content, encoding="utf-8")
            installed_files["split_layout"] = split_path

            # 2. Generate & write Konsole 4-tab layout .tabs file
            tabs_path = self.konsole_dir / f"{config.model_id}-4tabs.tabs"
            tabs_content = DesktopEntryGenerator.generate_tab_layout(config)
            tabs_path.write_text(tabs_content, encoding="utf-8")
            installed_files["tab_layout"] = tabs_path

            # 3. Handle icon file copy if local file path or bundled icon specified
            icon_setting = config.icon
            icon_path = None
            if icon_setting:
                expanded = Path(icon_setting).expanduser()
                if expanded.is_file():
                    icon_path = expanded
                else:
                    cand1 = ASSETS_ICONS_DIR / icon_setting
                    cand2 = ASSETS_ICONS_DIR / f"{icon_setting}.svg"
                    if cand1.is_file():
                        icon_path = cand1
                    elif cand2.is_file():
                        icon_path = cand2

            if icon_path and icon_path.is_file():
                try:
                    self.icons_dir.mkdir(parents=True, exist_ok=True)
                    target_icon_path = self.icons_dir / icon_path.name
                    shutil.copy2(icon_path, target_icon_path)
                    os.chmod(target_icon_path, 0o644)
                    installed_files["icon"] = target_icon_path
                    # Use absolute path for icon assignment
                    config.icon = str(target_icon_path.resolve())
                except OSError as e:
                    print(f"[!] Warning: Could not copy icon file: {e}", file=sys.stderr)
            elif not ASSETS_ICONS_DIR.exists():
                print(f"[!] Warning: Bundled icon assets directory '{ASSETS_ICONS_DIR}' not found.", file=sys.stderr)

            # 4. Generate & write .desktop entry referencing the layouts in Konsole Desktop Actions and absolute icon path
            desktop_file_path = self.apps_dir / config.desktop_filename
            desktop_content = DesktopEntryGenerator.generate_desktop_entry(
                config,
                konsole_dir=self.konsole_dir,
                icons_dir=self.icons_dir,
            )
            desktop_file_path.write_text(desktop_content, encoding="utf-8")
            os.chmod(desktop_file_path, 0o755)
            installed_files["desktop"] = desktop_file_path

            # 5. Optional Konsole profile
            if install_konsole_profile:
                profile_name = f"{config.model_id}.profile"
                konsole_file_path = self.konsole_dir / profile_name
                profile_content = DesktopEntryGenerator.generate_konsole_profile(config)
                konsole_file_path.write_text(profile_content, encoding="utf-8")
                installed_files["profile"] = konsole_file_path

        except Exception as e:
            print(f"[-] Failure during file installation for '{config.model_name}': {e}", file=sys.stderr)
            raise

        return installed_files

    @staticmethod
    def refresh_kde_cache() -> List[str]:
        """Execute KDE Plasma / XDG cache update tools with robust error handling."""
        results = []

        # 1. kbuildsycoca6 (KDE Plasma 6)
        if shutil.which("kbuildsycoca6"):
            try:
                res = subprocess.run(["kbuildsycoca6", "--noincremental"], capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    results.append("Successfully refreshed KDE Plasma 6 sycoca cache (kbuildsycoca6).")
                else:
                    results.append(f"kbuildsycoca6 returned exit code {res.returncode}: {res.stderr.strip()}")
            except subprocess.TimeoutExpired:
                results.append("kbuildsycoca6 command timed out after 10 seconds.")
            except Exception as e:
                results.append(f"Failed to execute kbuildsycoca6: {e}")
        elif shutil.which("kbuildsycoca5"):
            try:
                res = subprocess.run(["kbuildsycoca5", "--noincremental"], capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    results.append("Successfully refreshed KDE Plasma 5 sycoca cache (kbuildsycoca5).")
                else:
                    results.append(f"kbuildsycoca5 returned exit code {res.returncode}: {res.stderr.strip()}")
            except subprocess.TimeoutExpired:
                results.append("kbuildsycoca5 command timed out after 10 seconds.")
            except Exception as e:
                results.append(f"Failed to execute kbuildsycoca5: {e}")

        # 2. update-desktop-database (Standard XDG)
        if shutil.which("update-desktop-database"):
            apps_dir = str(LauncherInstaller.DEFAULT_APPS_DIR)
            try:
                res = subprocess.run(["update-desktop-database", apps_dir], capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    results.append(f"Successfully updated desktop database in {apps_dir}.")
                else:
                    results.append(f"update-desktop-database output: {res.stderr.strip()}")
            except Exception as e:
                results.append(f"Failed to execute update-desktop-database: {e}")

        if not results:
            results.append("No desktop database tools found (kbuildsycoca6 / update-desktop-database). Desktop files saved.")

        return results

    @staticmethod
    def print_taskbar_instructions(configs: List[LauncherConfig]) -> None:
        """Print clean, clear success instructions on dragging launchers to KDE taskbar panel."""
        print("\n" + "=" * 72)
        print("  🎉 INSTALLATION COMPLETE! HOW TO ADD TO YOUR KDE PLASMA TASKBAR PANEL")
        print("=" * 72)
        print("\nYour AI launchers are now installed and indexed in KDE Plasma 6:")
        for cfg in configs:
            print(f"  • {cfg.model_name} ({cfg.desktop_filename})")

        print("""
📌 STEP-BY-STEP INSTRUCTIONS:

  1. Open Application Launcher:
     Press the Meta/Super key or click the Application Launcher (Kickoff) icon in the panel.

  2. Locate Your AI Applications:
     Search for "Claude", "Antigravity", or "Codex" (or check under "Utilities" / "Development").

  3. Pin to Taskbar Panel:
     Right-click the application icon and select "Pin to Taskbar"
     (or drag and drop the icon directly onto your KDE Taskbar Panel).

  4. Right-Click Context Menu Actions:
     Left-click the pinned icon to launch a standard single terminal session.
     RIGHT-CLICK the taskbar icon to reveal KDE Desktop Actions:
       ┌────────────────────────────────────────────────────────┐
       │  ▶ Open Single Session                                 │
       │  🪟 Launch 4-Pane Split Grid   (--layout .json)        │
       │  📑 Launch 4-Tab Session      (--tabs-from-file .tabs)│
       │  📌 Unpin from Taskbar                                 │
       └────────────────────────────────────────────────────────┘
""")
