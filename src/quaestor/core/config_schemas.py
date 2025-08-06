"""Configuration schemas for Quaestor using Pydantic."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HooksConfig(BaseModel):
    """Hook system configuration."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    strict_mode: bool = False


class QuaestorMainConfig(BaseModel):
    """Main Quaestor configuration schema."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    hooks: HooksConfig = Field(default_factory=HooksConfig)


class LanguageConfig(BaseModel):
    """Language-specific configuration schema."""

    model_config = ConfigDict(extra="allow")  # Allow additional fields for extensibility

    primary_language: str
    lint_command: str | None = None
    format_command: str | None = None
    test_command: str | None = None
    coverage_command: str | None = None
    type_check_command: str | None = None
    security_scan_command: str | None = None
    profile_command: str | None = None
    coverage_threshold: int | None = Field(default=None, ge=0, le=100)
    type_checking: bool = False
    performance_target_ms: int | None = Field(default=None, ge=1)
    commit_prefix: str = "feat"
    quick_check_command: str | None = None
    full_check_command: str | None = None
    precommit_install_command: str | None = None
    doc_style_example: str | None = None

    @field_validator("coverage_threshold")
    @classmethod
    def validate_coverage_threshold(cls, v):
        """Validate coverage threshold is reasonable."""
        if v is not None and v > 95:
            # This is a warning, not an error - high thresholds are allowed
            pass
        return v


class LanguagesConfig(BaseModel):
    """Container for all language configurations."""

    model_config = ConfigDict(extra="forbid")

    languages: dict[str, LanguageConfig] = Field(default_factory=dict)

    def get_language_config(self, language: str) -> LanguageConfig | None:
        """Get configuration for a specific language."""
        return self.languages.get(language)

    def has_language(self, language: str) -> bool:
        """Check if a language configuration exists."""
        return language in self.languages


class ConfigValidationResult(BaseModel):
    """Result of configuration validation."""

    model_config = ConfigDict(extra="forbid")

    valid: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def has_issues(self) -> bool:
        """Check if there are any warnings or errors."""
        return len(self.warnings) > 0 or len(self.errors) > 0


class ConfigurationLayer(BaseModel):
    """Represents a single layer in the configuration hierarchy."""

    model_config = ConfigDict(extra="forbid")

    priority: int
    source: str
    description: str
    config_data: dict[str, Any] = Field(default_factory=dict)
    file_path: Path | None = None
    exists: bool = False

    def __lt__(self, other):
        """Sort by priority (lower number = higher priority)."""
        return self.priority < other.priority
