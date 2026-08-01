"""Configuration data schema for KDE AI Launcher entries."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import re


@dataclass
class LauncherConfig:
    """Data schema representing an AI CLI tool configuration for KDE Plasma 6."""

    model_name: str
    binary_command: str
    icon: str = "utilities-terminal"
    desktop_filename: str = ""
    comment: str = ""
    categories: List[str] = field(default_factory=lambda: ["Utility", "Development", "ConsoleOnly"])
    terminal: bool = True
    konsole_profile: Optional[str] = None

    def __post_init__(self) -> None:
        """Sanitize and set default desktop filename if not explicitly provided."""
        if not self.desktop_filename:
            sanitized = re.sub(r"[^\w\-]", "-", self.model_name.lower())
            sanitized = re.sub(r"-+", "-", sanitized).strip("-")
            self.desktop_filename = f"ai-{sanitized or 'launcher'}.desktop"
        elif not self.desktop_filename.endswith(".desktop"):
            self.desktop_filename = f"{self.desktop_filename}.desktop"

        if not self.comment:
            self.comment = f"Launch {self.model_name} in Konsole"

    @property
    def model_id(self) -> str:
        """Sanitized unique identifier string derived from model_name."""
        sanitized = re.sub(r"[^\w\-]", "-", self.model_name.lower())
        sanitized = re.sub(r"-+", "-", sanitized).strip("-")
        return sanitized or "ai-launcher"

    @property
    def wm_class(self) -> str:
        """WM_CLASS identifier for window manager taskbar association."""
        return f"ai-{self.model_id}"



    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LauncherConfig":
        """Construct LauncherConfig instance from dictionary."""
        return cls(
            model_name=data.get("model_name", "AI Assistant"),
            binary_command=data.get("binary_command", "aichat"),
            icon=data.get("icon", "utilities-terminal"),
            desktop_filename=data.get("desktop_filename", ""),
            comment=data.get("comment", ""),
            categories=data.get("categories", ["Utility", "Development", "ConsoleOnly"]),
            terminal=data.get("terminal", True),
            konsole_profile=data.get("konsole_profile"),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "LauncherConfig":
        """Deserialize LauncherConfig instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
