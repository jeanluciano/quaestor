"""Shared test fixtures for Quaestor tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
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


@pytest.fixture
def sample_memory_manifest() -> str:
    """Sample MEMORY.md content in manifest format."""
    return """# Project Memory & Progress Tracking

## Current Status
- **Last Updated**: 2024-01-15
- **Current Phase**: Development
- **Overall Progress**: 60%

## Project Timeline
### Milestone 1: Core Features (Complete)
- ✅ Basic order processing
- ✅ User authentication

### Milestone 2: Advanced Features (In Progress)
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
