#!/usr/bin/env python3
"""Main entry point for A1 service."""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

from a1.service.core import A1Service

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class A1ServiceRunner:
    """Runs the A1 service."""

    def __init__(self, config_path: Path, mode: str = "background"):
        """Initialize service runner.

        Args:
            config_path: Path to configuration file
            mode: Service mode (background or interactive)
        """
        self.config_path = config_path
        self.mode = mode
        self.service = None
        self.running = False

    async def start(self):
        """Start the A1 service."""
        logger.info(f"Starting A1 service in {self.mode} mode...")

        # Load configuration
        config = self._load_config()

        # Create and initialize service
        self.service = A1Service(config)
        await self.service.initialize()

        # Set up signal handlers
        self._setup_signal_handlers()

        # Start service
        await self.service.start()
        self.running = True

        # If interactive mode, start TUI dashboard
        if self.mode == "interactive":
            await self._start_dashboard()

        # Keep service running
        while self.running:
            await asyncio.sleep(1)

        # Shutdown
        await self.service.stop()
        logger.info("A1 service stopped")

    def _load_config(self) -> dict:
        """Load configuration from file.

        Returns:
            Configuration dict
        """
        try:
            if self.config_path.suffix == ".yaml":
                import yaml

                with open(self.config_path) as f:
                    config = yaml.safe_load(f)
                    return config.get("a1", {})
            else:
                import json

                with open(self.config_path) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return {}

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def _start_dashboard(self):
        """Start TUI dashboard in interactive mode."""
        # TODO: Implement TUI dashboard using Textual
        logger.info("TUI dashboard not yet implemented")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="A1 Service")
    parser.add_argument("--mode", choices=["background", "interactive"], default="background", help="Service mode")
    parser.add_argument("--config", type=Path, required=True, help="Path to configuration file")
    parser.add_argument("--dashboard", action="store_true", help="Start with dashboard (interactive mode only)")

    args = parser.parse_args()

    # Validate arguments
    if args.dashboard and args.mode != "interactive":
        logger.error("Dashboard requires interactive mode")
        sys.exit(1)

    if not args.config.exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)

    # Create and run service
    runner = A1ServiceRunner(args.config, args.mode)

    try:
        asyncio.run(runner.start())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
