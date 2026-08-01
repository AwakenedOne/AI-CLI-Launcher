# KDE AI Launcher (`kde-ai-launcher`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Target OS](https://img.shields.io/badge/OS-Ubuntu_24.04-orange.svg)](https://ubuntu.com)
[![KDE Plasma](https://img.shields.io/badge/KDE_Plasma-6.0+-blue.svg)](https://kde.org/plasma-desktop/)
[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://python.org)

---

## 📖 Overview

`kde-ai-launcher` is an open-source CLI utility for **Ubuntu 24.04 LTS** and **KDE Plasma 5/6** desktop power users. It creates native KDE taskbar shortcuts and application entries for **Claude**, **Antigravity**, and **Codex** CLI tools. 

Each shortcut includes KDE Plasma Desktop Actions that enable **right-click context menu options** to launch:
- **Single Terminal Session** (`konsole -e <binary>`)
- **2x2 Split Grid Layout** (`konsole --layout <model_id>-4split.json`) running 4 parallel AI panes
- **4-Tab Session** (`konsole --tabs-from-file <model_id>-4tabs.tabs`) running 4 titled AI tabs

---

## 📋 Prerequisites

Before installing `kde-ai-launcher`, ensure your system meets the following requirements:

- **Operating System**: Ubuntu 24.04 LTS (or any Linux distribution running KDE Plasma 5 or Plasma 6)
- **Terminal Emulator**: Konsole terminal emulator
- **Package Installer**: `pipx` installed via `apt`:

```bash
sudo apt update && sudo apt install -y pipx
pipx ensurepath
```

---

## 🚀 Installation (End-User Guide)

Follow these simple steps to install and configure `kde-ai-launcher`:

### 1. Install via `pipx`

Install the latest version directly from GitHub into an isolated environment using `pipx`:

```bash
# Install the tool via pipx
pipx install git+https://github.com/AwakenedOne/AI-CLI-Launcher.git
```

### 2. Run the Interactive Configuration Wizard

Launch the interactive setup wizard to configure **Claude**, **Antigravity**, and **Codex**:

```bash
# Run the launcher configuration wizard
kde-ai-launcher generate
```

*(You will be prompted for display names, binary commands, custom flags/arguments, and preferred icon styles.)*

### 3. Register Desktop Shortcuts & Refresh KDE Cache

Install the generated `.desktop` launchers and layout files to register them in KDE Plasma:

```bash
# Register desktop shortcuts and update KDE menu cache
kde-ai-launcher install
```

---

## 🖥️ KDE Plasma Taskbar Pinning & Context Menu Guide

Once `kde-ai-launcher install` finishes:

1. **Open Application Launcher**: Press `Meta` / `Super` or click the Application Launcher (Kickoff) icon on your KDE Panel.
2. **Find Your Applications**: Search for **Claude**, **Antigravity**, or **Codex** (or browse under *Utilities* / *Development*).
3. **Pin to Taskbar**: Right-click the application icon and select **"Pin to Taskbar"** (or drag and drop it onto the taskbar panel).
4. **Right-Click Context Menu**:
   - **Left-Click**: Launches a single terminal session.
   - **Right-Click**: Displays the KDE Desktop Actions menu:

```text
┌─────────────────────────────────────────────────────────────┐
│  ▶ Open Single Session                                      │
│  🪟 Launch 4-Pane Split Grid   (konsole --layout 4split)    │
│  📑 Launch 4-Tab Session      (konsole --tabs-from-file)   │
│  ──────────                                                 │
│  📌 Unpin from Taskbar                                      │
└─────────────────────────────────────────────────────────────┘
```

### Layout Overview Diagram

```text
[ Taskbar Icon ] ──( Right Click )──► ┌──────────────────────────────────────┐
                                     │ 🪟 Launch 4-Pane Split Grid         │
                                     │ 📑 Launch 4-Tab Session            │
                                     └──────────────────┬───────────────────┘
                                                        │
                      ┌─────────────────────────────────┴─────────────────────────────────┐
                      ▼                                                                   ▼
       ┌──────────────────────────────┐                                    ┌──────────────────────────────┐
       │      Konsole 2x2 Grid        │                                    │        Konsole Tabs          │
       │ ┌─────────────┬────────────┐ │                                    │ [Session 1][Session 2][...]  │
       │ │ Pane 1 (AI) │ Pane 2 (AI)│ │                                    │ ┌──────────────────────────┐ │
       │ ├─────────────┼────────────┤ │                                    │ │ Active Session (AI)      │ │
       │ │ Pane 3 (AI) │ Pane 4 (AI)│ │                                    │ └──────────────────────────┘ │
       │ └─────────────┴────────────┘ │                                    └──────────────────────────────┘
       └──────────────────────────────┘
---

## 🗑️ Uninstalling

To clean up and remove all generated desktop shortcuts, Konsole layouts, icons, and uninstall the package:

```bash
# Step 1: Remove generated desktop shortcuts, Konsole layouts, and icons
kde-ai-launcher uninstall

# Step 2: Uninstall the CLI package
pipx uninstall kde-ai-launcher
```

---

## 🛠️ Developers & Contributors Guide

### Editable Local Installation

```bash
git clone https://github.com/AwakenedOne/AI-CLI-Launcher.git
cd AI-CLI-Launcher

# Install in editable mode
pip install -e .

# Or run directly without installation
python3 main.py generate
```

### Running Test Suite

```bash
pip install -e ".[dev]"
python3 -m pytest
```

---

## 📁 Installed Asset Paths

- **Desktop Applications**: `~/.local/share/applications/ai-claude.desktop`, `ai-antigravity.desktop`, `ai-codex.desktop`
- **Konsole Split Layouts**: `~/.config/konsole/claude-4split.json`, `antigravity-4split.json`, `codex-4split.json`
- **Konsole Tab Layouts**: `~/.config/konsole/claude-4tabs.tabs`, `antigravity-4tabs.tabs`, `codex-4tabs.tabs`
- **Icon Files**: `~/.local/share/icons/claude.svg`, `antigravity.svg`, `codex.svg`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
