"""CLI entry point for kde-ai-launcher targeting Claude, Antigravity, and Codex."""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .config import LauncherConfig
from .installer import LauncherInstaller


ASSETS_ICONS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"


def get_default_icon_for_model(model_key: str) -> str:
    """Resolve default SVG icon path for target model (claude, antigravity, codex)."""
    icon_file = ASSETS_ICONS_DIR / f"{model_key.lower()}.svg"
    if icon_file.exists():
        return str(icon_file)
    return "utilities-terminal"


def prompt_user(text: str, default: str) -> str:
    """Prompt user for interactive input with default fallback."""
    response = input(f"{text} [{default}]: ").strip()
    return response if response else default


def prompt_icon_choice(model_key: str, default_option: str = "1") -> str:
    """Prompt user to choose an icon option: model-specific SVG, system icon name, or local file path."""
    default_svg = get_default_icon_for_model(model_key)
    svg_basename = Path(default_svg).name

    print(f"  Select Icon Option for {model_key.capitalize()}:")
    print(f"    [1] Dedicated model SVG icon ({svg_basename})")
    print("    [2] Standard system icon name (e.g., 'utilities-terminal', 'system-search')")
    print("    [3] Custom local file path (SVG/PNG)")
    choice = input(f"  Choice [1-3] (default: {default_option}): ").strip() or default_option

    if choice == "1":
        return default_svg
    elif choice == "2":
        icon_name = input("  Enter system icon name [utilities-terminal]: ").strip()
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


def interactive_wizard() -> List[LauncherConfig]:
    """Run interactive setup wizard to configure the 3 target AI models: Claude, Antigravity, and Codex."""
    print("=" * 72)
    print("  KDE AI Launcher - Interactive Setup Wizard (Claude, Antigravity, Codex)")
    print("  Targeting Ubuntu 24.04 LTS & KDE Plasma 6 Desktop Environment")
    print("=" * 72)
    print()

    target_models: List[Tuple[str, str, str, str]] = [
        ("Claude", "claude", "ai-claude.desktop", "claude"),
        ("Antigravity", "antigravity", "ai-antigravity.desktop", "antigravity"),
        ("Codex", "codex", "ai-codex.desktop", "codex"),
    ]

    configs: List[LauncherConfig] = []

    for idx, (def_name, def_cmd, def_file, key) in enumerate(target_models, start=1):
        print(f"\n--- Model {idx} of 3 Configuration ({def_name}) ---")
        model_name = prompt_user(f"Model {idx} Display Name", def_name)
        base_command = prompt_user(f"Model {idx} Executable Command", def_cmd)
        custom_args = input(f"Optional Flags/Arguments for {def_name} (e.g. --verbose or leave blank): ").strip()

        if custom_args:
            full_command = f"{base_command} {custom_args}"
        else:
            full_command = base_command

        first_word = base_command.split()[0] if base_command else ""
        if first_word and not shutil.which(first_word):
            print(f"  [!] Note: Binary '{first_word}' was not found in system PATH. Launcher will still be created.")

        icon = prompt_icon_choice(model_key=key, default_option="1")
        desktop_file = prompt_user(f"Target Desktop Filename", def_file)

        config = LauncherConfig(
            model_name=model_name,
            binary_command=full_command,
            icon=icon,
            desktop_filename=desktop_file,
        )
        configs.append(config)

    print("\n" + "=" * 72)
    print("  Generated Configurations Summary:")
    print("=" * 72)
    for idx, cfg in enumerate(configs, start=1):
        print(f"\nModel #{idx}: {cfg.model_name}")
        print(f"  Command:      {cfg.binary_command}")
        print(f"  Icon:         {cfg.icon}")
        print(f"  Desktop File: {cfg.desktop_filename}")

    return configs


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point for kde-ai-launcher."""
    parser = argparse.ArgumentParser(
        prog="kde-ai-launcher",
        description="Scaffold and install KDE Plasma 6 desktop launchers for Claude, Antigravity, and Codex CLI tools.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Run interactive wizard to configure Claude, Antigravity, and Codex.")
    gen_parser.add_argument("--out-dir", "-o", type=str, help="Export generated JSON configs to directory.")
    gen_parser.add_argument("--install", "-i", action="store_true", help="Install desktop entries immediately after wizard.")

    # Command: install
    inst_parser = subparsers.add_parser("install", help="Install desktop application entry and KDE profiles.")
    inst_parser.add_argument("--config", "-j", type=str, help="Path to JSON configuration file.")
    inst_parser.add_argument("--model-name", "-m", type=str, help="Model Name (e.g. 'Claude', 'Antigravity', 'Codex')")
    inst_parser.add_argument("--binary-command", "-c", type=str, help="Binary command (e.g. 'claude')")
    inst_parser.add_argument("--icon", type=str, help="System icon name or path")
    inst_parser.add_argument("--desktop-file", "-f", type=str, help="Target desktop filename")
    inst_parser.add_argument("--konsole-profile", action="store_true", help="Also generate and install KDE Konsole profile")

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "generate":
        configs = interactive_wizard()

        if parsed_args.out_dir:
            out_dir = Path(parsed_args.out_dir).expanduser()
            out_dir.mkdir(parents=True, exist_ok=True)
            for cfg in configs:
                out_path = out_dir / f"{cfg.model_id}.json"
                out_path.write_text(cfg.to_json(), encoding="utf-8")
                print(f"[+] Saved JSON config to: {out_path.resolve()}")

        if parsed_args.install or input("\nInstall all 3 launchers (Claude, Antigravity, Codex) now? [Y/n]: ").strip().lower() in ("", "y", "yes"):
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
        if parsed_args.config:
            config_path = Path(parsed_args.config).expanduser()
            if not config_path.exists():
                print(f"[-] Error: Config file '{config_path}' not found.", file=sys.stderr)
                return 1
            config = LauncherConfig.from_json(config_path.read_text(encoding="utf-8"))
        elif parsed_args.model_name and parsed_args.binary_command:
            icon_arg = parsed_args.icon
            if not icon_arg:
                icon_arg = get_default_icon_for_model(parsed_args.model_name)

            config = LauncherConfig(
                model_name=parsed_args.model_name,
                binary_command=parsed_args.binary_command,
                icon=icon_arg,
                desktop_filename=parsed_args.desktop_file or "",
            )
        else:
            print("[-] Error: Specify either --config <file.json> OR both --model-name and --binary-command", file=sys.stderr)
            return 1

        installer = LauncherInstaller()
        installed_files = installer.install(config, install_konsole_profile=parsed_args.konsole_profile)

        print("\nRefreshing KDE Plasma Desktop Cache...")
        cache_notes = installer.refresh_kde_cache()
        for note in cache_notes:
            print(f"  -> {note}")

        installer.print_taskbar_instructions([config])

    return 0


if __name__ == "__main__":
    sys.exit(main())
