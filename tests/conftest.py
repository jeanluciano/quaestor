"""Shared test fixtures for Quaestor tests."""

import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture(scope="session")
def sample_architecture_manifest() -> str:
    """Sample ARCHITECTURE.md content in manifest format."""
    return """# Project Architecture

## Architecture Overview
This project follows a Domain-Driven Design (DDD) approach to maintain clean separation of concerns.

## Core Concepts
The system is built around these key components:
- **Order Processing**: Handles order creation and management
- **Inventory Management**: Tracks product availability
- **Payment Processing**: Manages payment transactions

## System Layers
1. **Domain Layer**: Pure business logic
2. **Application Layer**: Use case orchestration
3. **Infrastructure Layer**: External integrations
"""


@pytest.fixture(scope="session")
def sample_memory_manifest() -> str:
    """Sample CONTEXT.md content in manifest format."""
    return """# Project Memory & Progress Tracking

## Current Status
- **Last Updated**: 2024-01-15
- **Current Phase**: Development
- **Overall Progress**: 60%

## Project Timeline
### Phase 1: Core Features (Complete)
- ✅ Basic order processing
- ✅ User authentication

### Phase 2: Advanced Features (In Progress)
- 🚧 Payment integration
- ⬜ Inventory tracking

## Next Actions
### Immediate (This Week)
1. Complete payment gateway integration
2. Add unit tests for order service
"""


@pytest.fixture
def mock_console(mocker):
    """Mock the rich console for testing."""
    return mocker.Mock()


@pytest.fixture
def temp_git_project(tmp_path):
    """Create a temporary project with git initialized."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Initialize git with minimal config for speed
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=project_dir, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_dir, check=True)
    # Disable git hooks for faster operations
    subprocess.run(["git", "config", "core.hooksPath", "/dev/null"], cwd=project_dir, check=True)

    # Create initial commit
    (project_dir / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit", "--no-verify"], cwd=project_dir, check=True)

    return project_dir


@pytest.fixture
def quaestor_project_with_files(temp_git_project):
    """Create a project with sample files for testing."""
    # Create source files
    src_dir = temp_git_project / "src"
    src_dir.mkdir()

    (src_dir / "__init__.py").write_text("")
    (src_dir / "main.py").write_text("""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def process_data(data: dict) -> Optional[dict]:
    '''Process incoming data.'''
    if not data:
        logger.warning("Empty data received")
        return None

    return {"processed": True, **data}

class DataProcessor:
    '''Main data processor class.'''

    def __init__(self, config: dict):
        self.config = config

    def run(self, items: list) -> list:
        '''Process a list of items.'''
        results = []
        for item in items:
            result = process_data(item)
            if result:
                results.append(result)
        return results
""")

    (src_dir / "utils.py").write_text("""
import os
from pathlib import Path

def get_project_root() -> Path:
    '''Get the project root directory.'''
    return Path(__file__).parent.parent

def load_config(config_path: str) -> dict:
    '''Load configuration from file.'''
    import json
    with open(config_path) as f:
        return json.load(f)
""")

    # Create test files
    tests_dir = temp_git_project / "tests"
    tests_dir.mkdir()

    (tests_dir / "test_main.py").write_text("""
import pytest
from src.main import process_data, DataProcessor

def test_process_data():
    result = process_data({"key": "value"})
    assert result == {"processed": True, "key": "value"}

def test_process_empty_data():
    assert process_data({}) is None

class TestDataProcessor:
    def test_init(self):
        processor = DataProcessor({"debug": True})
        assert processor.config["debug"] is True
""")

    # Create config files
    (temp_git_project / "requirements.txt").write_text("""
pytest>=7.0.0
pyyaml>=6.0
requests>=2.25.0
""")

    (temp_git_project / "pyproject.toml").write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
""")

    return temp_git_project


@pytest.fixture(scope="session")
def command_config_sample():
    """Sample command configuration data."""
    return {
        "commands": {
            "task": {
                "enforcement": "strict",
                "require_planning": True,
                "agent_threshold": 5,
                "parameters": {"minimum_test_coverage": 90, "max_function_lines": 30},
                "custom_rules": ["Always use type hints", "Document all public functions"],
            },
            "check": {"enforcement": "relaxed", "auto_fix": True},
            "specification": {"enforcement": "default", "parameters": {"auto_create_pr": True}},
        }
    }


@pytest.fixture
def mock_automation_context():
    """Mock context for automation hooks."""
    return {
        "tool": "Write",
        "file_path": "/test/file.py",
        "content": "print('test')",
        "timestamp": "2024-01-01T00:00:00",
        "session_id": "test-session",
        "metadata": {"user": "test", "project": "test-project"},
    }


@pytest.fixture(scope="session")
def mock_hook_result():
    """Mock hook result object."""

    class MockHookResult:
        def __init__(self, success=True, message="Success", data=None):
            self.success = success
            self.message = message
            self.data = data or {}

        def to_exit_code(self):
            return 0 if self.success else 1

    return MockHookResult


# Cache expensive imports at module level
_cached_modules = {}


@pytest.fixture(scope="session")
def cached_rich_console():
    """Cached Rich console for testing."""
    if "rich" not in _cached_modules:
        from rich.console import Console

        _cached_modules["rich"] = Console(force_terminal=False, width=80)
    return _cached_modules["rich"]


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """Configure environment for optimal test performance."""
    import os

    # Disable unnecessary features during tests
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["GIT_TERMINAL_PROMPT"] = "0"  # Disable git credential prompts

    # Set test-specific configurations
    os.environ["QUAESTOR_TEST_MODE"] = "1"

    yield

    # Cleanup
    os.environ.pop("QUAESTOR_TEST_MODE", None)
