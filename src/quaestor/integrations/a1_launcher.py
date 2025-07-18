"""A1 Launcher - Manages A1 service lifecycle from Quaestor."""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class A1Launcher:
    """Manages A1 service lifecycle from Quaestor."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize launcher with project root."""
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / ".quaestor" / "config.yaml"
        self.a1_config = None
        self.service_process = None
        
    def load_a1_config(self) -> Dict:
        """Load A1 configuration from Quaestor config.
        
        Returns:
            A1 configuration dict
        """
        try:
            # Try to load from YAML config
            if self.config_path.exists():
                import yaml
                with open(self.config_path) as f:
                    config = yaml.safe_load(f)
                    self.a1_config = config.get("a1", {})
            else:
                # Fallback to default config
                self.a1_config = self._get_default_config()
                
            return self.a1_config
            
        except Exception as e:
            logger.warning(f"Failed to load A1 config: {e}")
            self.a1_config = self._get_default_config()
            return self.a1_config
    
    def _get_default_config(self) -> Dict:
        """Get default A1 configuration.
        
        Returns:
            Default config dict
        """
        return {
            "enabled": False,
            "mode": "background",
            "components": {
                "event_system": {"enabled": True},
                "context_manager": {"enabled": True},
                "quality_guardian": {"enabled": True},
                "learning_manager": {"enabled": False},
                "analysis_engine": {"enabled": True}
            },
            "hooks": {
                "forward_to_a1": True,
                "receive_from_a1": True
            },
            "dashboard": {
                "enabled": False,
                "auto_start": False
            }
        }
    
    async def start_if_enabled(self) -> bool:
        """Start A1 service if configured to do so.
        
        Returns:
            True if service started or already running
        """
        config = self.load_a1_config()
        
        if not config.get("enabled", False):
            logger.info("A1 is not enabled in configuration")
            return False
            
        mode = config.get("mode", "background")
        
        if mode == "background":
            return await self._start_background_service()
        elif mode == "interactive":
            return await self._start_interactive_service()
        else:
            logger.warning(f"Unknown A1 mode: {mode}")
            return False
    
    async def _start_background_service(self) -> bool:
        """Start A1 in background mode (no UI).
        
        Returns:
            True if started successfully
        """
        try:
            logger.info("Starting A1 service in background mode...")
            
            # Prepare command
            cmd = [
                sys.executable, "-m", "a1.service.main",
                "--mode", "background",
                "--config", str(self.config_path)
            ]
            
            # Start service process
            self.service_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.5)
            
            # Check if it's running
            if self.service_process.poll() is None:
                logger.info(f"A1 service started (PID: {self.service_process.pid})")
                return True
            else:
                logger.error("A1 service failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start A1 service: {e}")
            return False
    
    async def _start_interactive_service(self) -> bool:
        """Start A1 with TUI dashboard.
        
        Returns:
            True if started successfully
        """
        try:
            logger.info("Starting A1 service in interactive mode...")
            
            # Prepare command
            cmd = [
                sys.executable, "-m", "a1.service.main",
                "--mode", "interactive",
                "--dashboard",
                "--config", str(self.config_path)
            ]
            
            # Start in new terminal window (platform-specific)
            if sys.platform == "darwin":  # macOS
                terminal_cmd = ["open", "-a", "Terminal.app"] + cmd
            elif sys.platform.startswith("linux"):
                terminal_cmd = ["x-terminal-emulator", "-e"] + cmd
            else:  # Windows
                terminal_cmd = ["start", "cmd", "/c"] + cmd
                
            subprocess.Popen(terminal_cmd)
            
            logger.info("A1 service launched in new terminal")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start A1 interactive service: {e}")
            return False
    
    async def stop_service(self):
        """Stop the A1 service if running."""
        if self.service_process and self.service_process.poll() is None:
            logger.info("Stopping A1 service...")
            self.service_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.service_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.service_process.kill()
                
            logger.info("A1 service stopped")
    
    def is_service_running(self) -> bool:
        """Check if A1 service is running.
        
        Returns:
            True if service is running
        """
        if self.service_process:
            return self.service_process.poll() is None
            
        # Check for service socket
        socket_path = Path.home() / ".quaestor" / "a1" / "service.sock"
        return socket_path.exists()
    
    def install_hooks(self) -> bool:
        """Install A1 hooks in Claude settings.
        
        Returns:
            True if installation successful
        """
        try:
            from a1.setup import A1HookInstaller
            
            installer = A1HookInstaller()
            return installer.install_hooks()
            
        except ImportError:
            logger.error("A1 not available for hook installation")
            return False
        except Exception as e:
            logger.error(f"Failed to install A1 hooks: {e}")
            return False


def add_a1_to_cli(app):
    """Add A1 commands to Quaestor CLI app.
    
    Args:
        app: Typer app instance
    """
    try:
        # Import A1 CLI if available
        from a1.cli import app as a1_app
        
        # Only add if A1 is enabled
        launcher = A1Launcher()
        config = launcher.load_a1_config()
        
        if config.get("enabled", False):
            app.add_typer(
                a1_app,
                name="a1",
                help="A1 automatic intelligence features",
                hidden=False
            )
            logger.info("A1 CLI commands added")
        else:
            # Add hidden placeholder
            app.add_typer(
                a1_app,
                name="a1",
                help="A1 automatic intelligence (disabled)",
                hidden=True
            )
            
    except ImportError:
        # A1 not available
        logger.debug("A1 module not available")