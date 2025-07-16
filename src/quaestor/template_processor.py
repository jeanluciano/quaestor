"""Legacy template processor - redirects to new simplified processor."""

from pathlib import Path
from typing import Any

from .templates.processor import get_project_data as _get_project_data
from .templates.processor import process_template as _process_template


def get_project_data(project_dir: Path) -> dict[str, Any]:
    """Get project data for template rendering.

    This is a legacy wrapper around the new simplified processor.
    """
    return _get_project_data(project_dir)


def process_template(template_path: Path, project_data: dict[str, Any]) -> str:
    """Process a template file with project data.

    This is a legacy wrapper around the new simplified processor.
    """
    return _process_template(template_path, project_data)
