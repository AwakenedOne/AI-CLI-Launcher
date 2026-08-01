"""CLI entry point for kde-ai-launcher targeting Claude, Antigravity, and Codex."""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .config import LauncherConfig
from .installer import LauncherInstaller


ASSETS_ICONS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"
if not ASSETS_ICONS_DIR.exists():
    ASSETS_ICONS_DIR = Path(__file__).resolve().parent / "assets" / "icons"

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "kde-ai-launcher"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"


def get_default_icon_for_model(model_key: str) -> str:
    """Resolve default SVG icon path for target model (claude, antigravity, codex)."""
    icon_file = ASSETS_ICONS_DIR / f"{model_key.lower()}.svg"
    if icon_file.exists():
        return str(icon_file)
    return "utilities-terminal"


def prompt_user(text: str, default: str) -> str:
    """Prompt user for interactive input with default fallback."""
    response = input(f"{text} [default: {default}]: ").strip()
    return response if response else default


def prompt_icon_choice(model_key: str, default_option: str = "1") -> str:
    """Prompt user to choose an icon option: model-specific SVG, system icon name, or local file path."""
    default_svg = get_default_icon_for_model(model_key)
    svg_basename = Path(default_svg).name

    print(f"  Select Icon Option for {model_key.capitalize()}:")
    print(f"    [1] Dedicated model SVG icon ({svg_basename})")
    print("    [2] Standard system icon name (e.g., 'utilities-terminal', 'system-search')")
    print("    [3] Custom local file path (SVG/PNG)")
    choice = input(f"  Choice [1-3] [default: {default_option}]: ").strip() or default_option

    if choice == "1":
        return default_svg
    elif choice == "2":
        icon_name = input("  Enter system icon name [default: utilities-terminal]: ").strip()
        return icon_name if icon_name else "utilities-terminal"
    elif choice == "3":
        file_path = input("  Enter local icon file path: ").strip()
        expanded = Path(file_path).expanduser()
        if not expanded.exists():
            print(f"  [!] Warning: File '{file_path}' does not exist. Falling back to dedicated icon '{svg_basename}'.", file=sys.stderr)
            return default_svg
        return str(expanded)
    else:
        print(f"  [!] Invalid choice. Defaulting to dedicated icon '{svg_basename}'.")
        return default_svg


def get_default_configs() -> List[LauncherConfig]:
    """Generate default non-interactive configurations for Claude, Antigravity, and Codex."""
    return [
        LauncherConfig(
            model_name="Claude",
            binary_command="claude",
            icon=get_default_icon_for_model("claude"),
            desktop_filename="ai-claude.desktop",
        ),
        LauncherConfig(
            model_name="Antigravity",
            binary_command="agy",
            icon=get_default_icon_for_model("antigravity"),
            desktop_filename="ai-antigravity.desktop",
        ),
        LauncherConfig(
            model_name="Codex",
            binary_command="codex",
            icon=get_default_icon_for_model("codex"),
            desktop_filename="ai-codex.desktop",
        ),
    ]


def save_saved_configs(configs: List[LauncherConfig], file_path: Optional[Path] = None) -> Path:
    """Save generated launcher configurations to JSON file (default ~/.config/kde-ai-launcher/config.json)."""
    target_path = (file_path or DEFAULT_CONFIG_FILE).expanduser()
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        data = [cfg.to_dict() for cfg in configs]
        target_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"[!] Warning: Could not save config file to '{target_path}': {e}", file=sys.stderr)
    return target_path


def load_saved_configs(file_path: Optional[Path] = None) -> List[LauncherConfig]:
    """Load saved launcher configurations from JSON file or fall back to default configs."""
    target_path = (file_path or DEFAULT_CONFIG_FILE).expanduser()
    if target_path.exists():
        try:
            content = target_path.read_text(encoding="utf-8")
            raw_data = json.loads(content)
            if isinstance(raw_data, list):
                return [LauncherConfig.from_dict(d) for d in raw_data]
            elif isinstance(raw_data, dict):
                return [LauncherConfig.from_dict(raw_data)]
        except Exception as e:
            print(f"[!] Warning: Could not read config file '{target_path}': {e}. Using default values.", file=sys.stderr)

    return get_default_configs()


def interactive_wizard() -> List[LauncherConfig]:
    """Run interactive setup wizard to configure the 3 target AI models: Claude, Antigravity, and Codex."""
    print("=" * 72)
    print("  KDE AI Launcher - Advanced Interactive Wizard")
    print("  Targeting Ubuntu 24.04 LTS & KDE Plasma 6 Desktop Environment")
    print("=" * 72)
    print()

    target_models: List[Tuple[str, str, str, str]] = [
        ("Claude", "claude", "ai-claude.desktop", "claude"),
        ("Antigravity", "agy", "ai-antigravity.desktop", "antigravity"),
        ("Codex", "codex", "ai-codex.desktop", "codex"),
    ]

    configs: List[LauncherConfig] = []

    for idx, (def_name, def_cmd, def_file, key) in enumerate(target_models, start=1):
        print(f"\n--- Model #{idx}: {def_name} Configuration ---")
        model_name = prompt_user("Model Display Name", def_name)
        base_command = prompt_user("Executable command", def_cmd)
        custom_args = input(f"Optional flags/arguments for {model_name} (leave blank for none): ").strip()

        if custom_args:
            full_command = f"{base_command} {custom_args}"
        else:
            full_command = base_command

        first_word = base_command.split()[0] if base_command else ""
        if first_word and not shutil.which(first_word):
            print(f"  [!] Note: Binary '{first_word}' was not found in system PATH. Launcher will still be created.")

        desktop_file = prompt_user("Desktop filename", def_file)
        if not desktop_file.endswith(".desktop"):
            desktop_file = f"{desktop_file}.desktop"

        default_icon = get_default_icon_for_model(key)
        svg_name = Path(default_icon).name
        change_icon = input(f"Custom icon? (default: bundled {svg_name}) [y/N]: ").strip().lower()
        if change_icon in ("y", "yes"):
            icon = prompt_icon_choice(model_key=key, default_option="1")
        else:
            icon = default_icon

        config = LauncherConfig(
            model_name=model_name,
            binary_command=full_command,
            icon=icon,
            desktop_filename=desktop_file,
        )
        configs.append(config)

    return configs


def print_summary(configs: List[LauncherConfig], title: str = "Generated Configurations Summary") -> None:
    """Print clean, friendly summary output of launcher configurations."""
    print("\n" + "=" * 72)
    print(f"  {title}:")
    print("=" * 72)
    for idx, cfg in enumerate(configs, start=1):
        print(f"\nModel #{idx}: {cfg.model_name}")
        print(f"  Command:      {cfg.binary_command}")
        print(f"  Icon:         {cfg.icon}")
        print(f"  Desktop File: {cfg.desktop_filename}")


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point for kde-ai-launcher."""
    parser = argparse.ArgumentParser(
        prog="kde-ai-launcher",
        description="Scaffold and install KDE Plasma desktop launchers for Claude, Antigravity, and Codex CLI tools.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Build KDE desktop launchers for Claude, Antigravity, and Codex.")
    gen_parser.add_argument("--advanced", "-a", action="store_true", help="Run interactive prompt for custom model settings.")
    gen_parser.add_argument("--out-dir", "-o", type=str, help="Export generated JSON configs to directory.")
    gen_parser.add_argument("--install", "-i", action="store_true", help="Install desktop entries immediately.")

    # Command: install
    inst_parser = subparsers.add_parser("install", help="Install desktop application entry and KDE profiles.")
    inst_parser.add_argument("--config", "-j", type=str, help="Path to JSON configuration file.")
    inst_parser.add_argument("--model-name", "-m", type=str, help="Model Name (e.g. 'Claude', 'Antigravity', 'Codex')")
    inst_parser.add_argument("--binary-command", "-c", type=str, help="Binary command (e.g. 'claude')")
    inst_parser.add_argument("--icon", type=str, help="System icon name or path")
    inst_parser.add_argument("--desktop-file", "-f", type=str, help="Target desktop filename")
    inst_parser.add_argument("--konsole-profile", action="store_true", help="Also generate and install KDE Konsole profile")

    # Command: uninstall
    uninst_parser = subparsers.add_parser("uninstall", help="Uninstall and remove all generated KDE desktop shortcuts, layout files, and icons.")
    uninst_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt.")

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "generate":
        if parsed_args.advanced:
            configs = interactive_wizard()
            print_summary(configs, "Advanced Configurations Summary")
            should_install = parsed_args.install or input("\nInstall all 3 launchers (Claude, Antigravity, Codex) now? [Y/n]: ").strip().lower() in ("", "y", "yes")
        else:
            print("=" * 72)
            print("  KDE AI Launcher - Zero-Config Setup (Claude, Antigravity, Codex)")
            print("=" * 72)
            configs = get_default_configs()
            print_summary(configs, "Generated Configurations Summary")
            should_install = True

        saved_path = save_saved_configs(configs)
        print(f"\n[+] Saved configuration layout to: {saved_path}")

        if parsed_args.out_dir:
            out_dir = Path(parsed_args.out_dir).expanduser()
            out_dir.mkdir(parents=True, exist_ok=True)
            for cfg in configs:
                out_path = out_dir / f"{cfg.model_id}.json"
                out_path.write_text(cfg.to_json(), encoding="utf-8")
                print(f"[+] Exported JSON config to: {out_path.resolve()}")

        if should_install:
            installer = LauncherInstaller()
            installed_all = []
            for cfg in configs:
                installed_files = installer.install(cfg)
                installed_all.append((cfg, installed_files))

            print("\nRefreshing KDE Plasma Desktop Cache...")
            cache_notes = installer.refresh_kde_cache()
            for note in cache_notes:
                print(f"  -> {note}")

            installer.print_taskbar_instructions([cfg for cfg, _ in installed_all])

    elif parsed_args.command == "install":
        configs_to_install: List[LauncherConfig] = []

        if parsed_args.config:
            config_path = Path(parsed_args.config).expanduser()
            if not config_path.exists():
                print(f"[-] Error: Config file '{config_path}' not found.", file=sys.stderr)
                return 1
            configs_to_install = load_saved_configs(config_path)
        elif parsed_args.model_name and parsed_args.binary_command:
            icon_arg = parsed_args.icon
            if not icon_arg:
                icon_arg = get_default_icon_for_model(parsed_args.model_name)

            configs_to_install = [
                LauncherConfig(
                    model_name=parsed_args.model_name,
                    binary_command=parsed_args.binary_command,
                    icon=icon_arg,
                    desktop_filename=parsed_args.desktop_file or "",
                )
            ]
        else:
            # Zero-config install: Load saved config or fall back to defaults
            configs_to_install = load_saved_configs()

        installer = LauncherInstaller()
        installed_all = []
        for cfg in configs_to_install:
            installed_files = installer.install(cfg, install_konsole_profile=parsed_args.konsole_profile)
            installed_all.append((cfg, installed_files))

        print("\nRefreshing KDE Plasma Desktop Cache...")
        cache_notes = installer.refresh_kde_cache()
        for note in cache_notes:
            print(f"  -> {note}")

        installer.print_taskbar_instructions([cfg for cfg, _ in installed_all])

    elif parsed_args.command == "uninstall":
        print("=" * 72)
        print("  KDE AI Launcher - Uninstallation")
        print("=" * 72)

        if not parsed_args.yes:
            confirm = input("Remove all generated desktop shortcuts, layout files, and model icons? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Uninstallation cancelled.")
                return 0

        installer = LauncherInstaller()
        removed_files = installer.uninstall()

        # Also remove saved config file if present
        if DEFAULT_CONFIG_FILE.exists():
            try:
                DEFAULT_CONFIG_FILE.unlink()
                removed_files.append(DEFAULT_CONFIG_FILE)
            except OSError:
                pass

        if removed_files:
            print("\n[+] Successfully removed the following launcher files:")
            for p in removed_files:
                print(f"  - {p}")
        else:
            print("\n[i] No existing launcher files were found to remove.")

        print("\nRefreshing KDE Plasma Desktop Cache...")
        cache_notes = installer.refresh_kde_cache()
        for note in cache_notes:
            print(f"  -> {note}")

        print("\n✨ Uninstallation complete! Shortcuts, layout files, and icons removed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
