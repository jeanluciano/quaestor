"""A1 Hook Installer - Installs A1 hooks in Claude Code settings."""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class A1HookInstaller:
    """Installs and manages A1 hooks in Claude Code settings."""
    
    # Hook command template
    HOOK_COMMAND_TEMPLATE = "python -m a1.hooks.claude_receiver {hook_type}"
    
    # All Claude Code hooks A1 can listen to
    CLAUDE_HOOKS = [
        "preStopHook",
        "stopHook", 
        "preToolUseHook",
        "postToolUseHook",
        "preFileEditHook",
        "postFileEditHook",
        "preUserPromptSubmitHook",
        "preProcessTextGenerationHook",
        "fileChangeHook",
        "testRunHook"
    ]
    
    # Map Claude hook names to our receiver method names
    HOOK_TYPE_MAP = {
        "preStopHook": "pre_stop",
        "stopHook": "stop",
        "preToolUseHook": "pre_tool_use",
        "postToolUseHook": "post_tool_use",
        "preFileEditHook": "pre_file_edit",
        "postFileEditHook": "post_file_edit",
        "preUserPromptSubmitHook": "pre_user_prompt",
        "preProcessTextGenerationHook": "pre_text_gen",
        "fileChangeHook": "file_change",
        "testRunHook": "test_run"
    }
    
    def __init__(self, claude_settings_path: Optional[Path] = None):
        """Initialize installer with Claude settings path."""
        if claude_settings_path is None:
            # Default location
            claude_settings_path = Path.cwd() / ".claude" / "settings.json"
        self.settings_path = claude_settings_path
        
    def install_hooks(self, backup: bool = True) -> bool:
        """Install A1 hooks in Claude settings.
        
        Args:
            backup: Whether to backup existing settings
            
        Returns:
            True if installation successful
        """
        try:
            # Ensure .claude directory exists
            self.settings_path.parent.mkdir(exist_ok=True)
            
            # Load existing settings
            settings = self._load_settings()
            
            # Backup if requested
            if backup and self.settings_path.exists():
                backup_path = self.settings_path.with_suffix(".json.bak")
                self.settings_path.rename(backup_path)
                logger.info(f"Backed up settings to {backup_path}")
                # Recreate settings file
                self._save_settings(settings)
            
            # Add A1 hooks
            hooks_added = self._add_a1_hooks(settings)
            
            # Save updated settings
            self._save_settings(settings)
            
            logger.info(f"Installed {hooks_added} A1 hooks in {self.settings_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install hooks: {e}")
            return False
    
    def uninstall_hooks(self) -> bool:
        """Remove A1 hooks from Claude settings.
        
        Returns:
            True if removal successful
        """
        try:
            settings = self._load_settings()
            hooks_removed = self._remove_a1_hooks(settings)
            self._save_settings(settings)
            
            logger.info(f"Removed {hooks_removed} A1 hooks from {self.settings_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall hooks: {e}")
            return False
    
    def check_installation(self) -> Dict[str, bool]:
        """Check which A1 hooks are installed.
        
        Returns:
            Dict mapping hook names to installation status
        """
        settings = self._load_settings()
        hooks = settings.get("hooks", {})
        
        status = {}
        for hook_name in self.CLAUDE_HOOKS:
            hook_value = hooks.get(hook_name, "")
            status[hook_name] = "a1.hooks.claude_receiver" in hook_value
            
        return status
    
    def _load_settings(self) -> Dict:
        """Load Claude settings from file.
        
        Returns:
            Settings dict (empty dict if file doesn't exist)
        """
        if not self.settings_path.exists():
            return {}
            
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
            return {}
    
    def _save_settings(self, settings: Dict):
        """Save settings to file.
        
        Args:
            settings: Settings dict to save
        """
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def _add_a1_hooks(self, settings: Dict) -> int:
        """Add A1 hooks to settings.
        
        Args:
            settings: Settings dict to modify
            
        Returns:
            Number of hooks added
        """
        if "hooks" not in settings:
            settings["hooks"] = {}
            
        hooks_added = 0
        
        for hook_name in self.CLAUDE_HOOKS:
            hook_type = self.HOOK_TYPE_MAP[hook_name]
            a1_command = self.get_hook_command(hook_type)
            
            existing = settings["hooks"].get(hook_name, "")
            
            if existing:
                # Chain with existing hook if not already present
                if "a1.hooks.claude_receiver" not in existing:
                    # Use && to chain commands
                    settings["hooks"][hook_name] = f"{existing} && {a1_command}"
                    hooks_added += 1
            else:
                # Add new hook
                settings["hooks"][hook_name] = a1_command
                hooks_added += 1
                
        return hooks_added
    
    def _remove_a1_hooks(self, settings: Dict) -> int:
        """Remove A1 hooks from settings.
        
        Args:
            settings: Settings dict to modify
            
        Returns:
            Number of hooks removed
        """
        if "hooks" not in settings:
            return 0
            
        hooks_removed = 0
        
        for hook_name in self.CLAUDE_HOOKS:
            if hook_name in settings["hooks"]:
                hook_value = settings["hooks"][hook_name]
                
                if "a1.hooks.claude_receiver" in hook_value:
                    # Remove A1 command
                    parts = hook_value.split(" && ")
                    remaining = [p for p in parts if "a1.hooks.claude_receiver" not in p]
                    
                    if remaining:
                        settings["hooks"][hook_name] = " && ".join(remaining)
                    else:
                        del settings["hooks"][hook_name]
                        
                    hooks_removed += 1
                    
        return hooks_removed
    
    def get_hook_command(self, hook_type: str) -> str:
        """Get the command for a specific hook type.
        
        Args:
            hook_type: Type of hook (e.g., "pre_tool_use")
            
        Returns:
            Command string
        """
        # Use sys.executable to ensure correct Python interpreter
        return f"{sys.executable} -m a1.hooks.claude_receiver {hook_type}"


def main():
    """CLI for hook installation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install/uninstall A1 hooks")
    parser.add_argument("action", choices=["install", "uninstall", "check"],
                       help="Action to perform")
    parser.add_argument("--settings-path", type=Path,
                       help="Path to Claude settings.json")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't backup settings when installing")
    
    args = parser.parse_args()
    
    installer = A1HookInstaller(args.settings_path)
    
    if args.action == "install":
        success = installer.install_hooks(backup=not args.no_backup)
        sys.exit(0 if success else 1)
    elif args.action == "uninstall":
        success = installer.uninstall_hooks()
        sys.exit(0 if success else 1)
    elif args.action == "check":
        status = installer.check_installation()
        print("A1 Hook Installation Status:")
        for hook, installed in status.items():
            print(f"  {hook}: {'✓' if installed else '✗'}")


if __name__ == "__main__":
    main()