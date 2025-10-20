"""Pytest fixtures for evaluation tests."""

import subprocess
from datetime import datetime

import pytest


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with .quaestor structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create .quaestor directory structure
    quaestor_dir = project_dir / ".quaestor"
    specs_dir = quaestor_dir / "specs"
    (specs_dir / "draft").mkdir(parents=True)
    (specs_dir / "active").mkdir(parents=True)
    (specs_dir / "completed").mkdir(parents=True)
    (specs_dir / "archived").mkdir(parents=True)

    return project_dir


@pytest.fixture
def temp_git_project(tmp_path):
    """Create a temporary project with git initialized."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)

    # Initialize git with minimal config for speed
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=project_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project_dir,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project_dir,
        check=True,
    )
    # Disable git hooks for faster operations
    subprocess.run(
        ["git", "config", "core.hooksPath", "/dev/null"],
        cwd=project_dir,
        check=True,
    )

    # Create initial commit
    (project_dir / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit", "--no-verify"],
        cwd=project_dir,
        check=True,
    )

    # Create .quaestor structure
    quaestor_dir = project_dir / ".quaestor"
    specs_dir = quaestor_dir / "specs"
    (specs_dir / "draft").mkdir(parents=True, exist_ok=True)
    (specs_dir / "active").mkdir(parents=True, exist_ok=True)
    (specs_dir / "completed").mkdir(parents=True, exist_ok=True)
    (specs_dir / "archived").mkdir(parents=True, exist_ok=True)

    return project_dir


@pytest.fixture
def good_quality_spec(temp_project):
    """Create a high-quality specification file for testing.

    This spec should score well on all quality metrics:
    - Complete and clear description
    - Well-defined acceptance criteria
    - Comprehensive test scenarios
    - Detailed contract
    """
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    spec_path = temp_project / ".quaestor/specs/draft" / f"{spec_id}.md"

    content = f"""---
id: {spec_id}
title: Add dark mode toggle to settings page
type: feature
status: draft
priority: medium
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
estimated_hours: 4
---

# Specification: Add dark mode toggle to settings page

## Description

Implement a dark mode toggle in the user settings page that allows users to switch between light
and dark themes. The preference should persist across sessions using localStorage, and the dark mode
styling should be applied immediately when toggled.

## Rationale

Dark mode is increasingly expected by users and can reduce eye strain in low-light environments.
It's also a common accessibility feature that improves the user experience. Many users have requested
this feature, and it's relatively straightforward to implement.

## Use Cases

- User wants to reduce eye strain while working at night
- User prefers dark interfaces for aesthetic reasons
- User wants consistent theming across different applications

## Contract

### Inputs
- `theme`: string ("light" | "dark")
- `userId`: string (for preference storage)

### Outputs
- `themeApplied`: boolean (whether theme was successfully applied)
- `preferenceSaved`: boolean (whether preference was saved to storage)

### Behavior
1. When toggle is clicked, switch theme immediately
2. Update localStorage with preference
3. Apply CSS classes to body element
4. Emit theme-change event for other components

### Constraints
- Must work in all supported browsers (Chrome, Firefox, Safari, Edge)
- Theme must persist across page reloads
- No flash of unstyled content on page load
- Performance impact must be < 50ms

### Error Handling
- `localStorage_unavailable`: Fall back to session-only theme
- `invalid_theme_value`: Default to light mode
- `css_load_failure`: Log error, continue with inline styles

## Acceptance Criteria

- [ ] Settings page displays a toggle switch labeled "Dark Mode"
- [ ] Clicking the toggle immediately switches between light and dark themes
- [ ] Theme preference is saved to localStorage
- [ ] Theme preference persists across browser sessions
- [ ] Dark mode CSS is properly applied to all UI components
- [ ] Toggle state reflects the current theme
- [ ] Theme is applied before page render (no flash)
- [ ] Unit tests verify toggle functionality
- [ ] Integration tests verify persistence
- [ ] Documentation updated with dark mode usage

## Test Scenarios

### Scenario 1: Toggle dark mode on
**Given:** User is on settings page with light mode active
**When:** User clicks the dark mode toggle switch
**Then:**
- Dark mode CSS is applied immediately
- All UI components display with dark theme colors
- localStorage contains theme="dark"
- Toggle switch shows "on" state

**Examples:**
- Background color changes from white (#ffffff) to dark gray (#1a1a1a)
- Text color changes from black (#000000) to light gray (#e0e0e0)

### Scenario 2: Persist theme across sessions
**Given:** User has enabled dark mode
**When:** User closes and reopens the browser
**Then:**
- Dark mode is still active
- No flash of light theme occurs
- localStorage still contains theme="dark"

### Scenario 3: Handle localStorage unavailable
**Given:** localStorage is disabled or unavailable
**When:** User toggles dark mode
**Then:**
- Theme switches for current session only
- Warning is logged to console
- User is notified that preference won't persist

## Dependencies

### Requires
- CSS framework supports theming (existing)
- localStorage API available in target browsers (existing)

### Blocks
- None

### Related
- Could be extended to support auto-detection of system theme preference
- Future: Custom theme builder feature

## Risks

### Risk 1: Browser compatibility
**Likelihood:** Low
**Impact:** Medium
**Mitigation:** Test in all supported browsers, provide fallbacks

### Risk 2: Performance impact
**Likelihood:** Low
**Impact:** Low
**Mitigation:** Lazy-load dark mode CSS, use CSS variables for instant switching

## Success Metrics

- 100% of acceptance criteria met
- All unit and integration tests passing
- Page load time increase < 50ms
- Zero console errors in supported browsers
- User feedback rating > 4.5/5

## Implementation Notes

This specification is ready for implementation. The implementing-features skill can begin work immediately.
"""

    spec_path.write_text(content)
    return spec_path


@pytest.fixture
def poor_quality_spec(temp_project):
    """Create a poor-quality specification file for testing.

    This spec should score poorly on quality metrics:
    - Vague description
    - Missing acceptance criteria
    - No test scenarios
    - Incomplete contract
    """
    import time

    time.sleep(1)  # Ensure different timestamp
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    spec_path = temp_project / ".quaestor/specs/draft" / f"poor-{spec_id}.md"

    content = f"""---
id: {spec_id}
title: Make app better
type: feature
status: draft
priority: low
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
---

# Specification: Make app better

## Description

Improve the app.

## Rationale

Users want it better.

## Contract

### Behavior
- Make improvements

## Acceptance Criteria

- [ ] App is better

## Test Scenarios

### Scenario 1: Test improvement
**Given:** App exists
**When:** Improvements applied
**Then:** App is better
"""

    spec_path.write_text(content)
    return spec_path


@pytest.fixture
def edge_case_spec(temp_project):
    """Create an edge case specification (very long, complex) for testing."""
    import time

    time.sleep(2)  # Ensure different timestamp
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    spec_path = temp_project / ".quaestor/specs/draft" / f"edge-{spec_id}.md"

    # Create a spec with nested lists and complex structure
    acceptance_criteria = "\n".join([f"- [ ] Criterion {i}" for i in range(1, 21)])

    content = f"""---
id: {spec_id}
title: Complex multi-component evaluation framework with extensive features
type: feature
status: draft
priority: critical
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
estimated_hours: 120
---

# Specification: Complex multi-component evaluation framework

## Description

Implement a comprehensive evaluation framework using Pydantic AI evals that supports multiple testing
paradigms, custom evaluators, dataset management, CI/CD integration, real-time monitoring, historical
tracking, and automated reporting across all skills, commands, and subagents in the system.

## Rationale

Quality assurance is critical for maintaining high standards in AI-assisted development workflows.
A robust evaluation framework enables data-driven improvements, regression detection, and continuous
benchmarking.

## Acceptance Criteria

{acceptance_criteria}

## Test Scenarios

### Scenario 1: Run comprehensive evaluation suite
**Given:** Evaluation framework is installed and configured
**When:** pytest tests/evals/ is executed
**Then:** All evaluations complete successfully with detailed reports

### Scenario 2: Handle evaluation failures gracefully
**Given:** A skill produces invalid output
**When:** Evaluation runs against the output
**Then:** Failure is logged with clear error message and suggestions

### Scenario 3: Generate historical comparison reports
**Given:** Multiple evaluation runs exist
**When:** Report generation is triggered
**Then:** Trends and regressions are clearly visualized

## Contract

### Inputs
- `evaluation_target`: string (skill, command, or agent name)
- `dataset`: list of test cases
- `evaluators`: list of evaluator functions

### Outputs
- `results`: evaluation results object
- `score`: float (0.0-1.0)
- `report`: markdown formatted report

### Behavior
1. Load dataset and evaluators
2. Execute target against each test case
3. Apply evaluators to outputs
4. Aggregate scores and generate report
5. Store results for historical tracking

### Constraints
- Must complete within 30 minutes
- Memory usage < 2GB
- Support concurrent evaluation execution
"""

    spec_path.write_text(content)
    return spec_path


@pytest.fixture
def active_spec_with_progress(temp_project):
    """Create an active specification with partial progress for testing."""
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}-active"
    spec_path = temp_project / ".quaestor/specs/active" / f"{spec_id}.md"

    content = f"""---
id: {spec_id}
title: User authentication system
type: feature
status: active
priority: high
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
estimated_hours: 16
---

# Specification: User authentication system

## Description

Implement a secure user authentication system with login, logout, password reset, and session management capabilities.

## Rationale

User authentication is a core requirement for the application to support personalized experiences and protect user data.

## Acceptance Criteria

- [x] Login endpoint implemented
- [x] Logout endpoint implemented
- [ ] Password reset flow implemented
- [ ] Session management with JWT tokens
- [ ] Password hashing with bcrypt
- [x] Unit tests for auth service
- [ ] Integration tests for auth endpoints
- [ ] Documentation for auth API

## Test Scenarios

### Scenario 1: User logs in successfully
**Given:** User has valid credentials
**When:** User submits login form
**Then:** JWT token is returned and session is created

## Contract

### Inputs
- `email`: string
- `password`: string

### Outputs
- `token`: JWT string
- `user`: User object

### Behavior
1. Validate credentials
2. Generate JWT token
3. Create session
4. Return token and user data
"""

    spec_path.write_text(content)
    return spec_path


@pytest.fixture
def completed_spec(temp_project):
    """Create a completed specification for testing."""
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}-completed"
    spec_path = temp_project / ".quaestor/specs/completed" / f"{spec_id}.md"

    content = f"""---
id: {spec_id}
title: Add search functionality
type: feature
status: completed
priority: medium
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
estimated_hours: 8
---

# Specification: Add search functionality

## Description

Add full-text search capability to the application with filtering and sorting options.

## Rationale

Users need to quickly find specific items in large datasets.

## Acceptance Criteria

- [x] Search input field added to UI
- [x] Search API endpoint implemented
- [x] Results display with highlighting
- [x] Filter by category
- [x] Sort by relevance or date
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Documentation complete

## Test Scenarios

### Scenario 1: Search returns relevant results
**Given:** Database contains searchable items
**When:** User enters search query
**Then:** Relevant results are returned and highlighted

## Contract

### Inputs
- `query`: string
- `filters`: optional object
- `sort`: optional string

### Outputs
- `results`: array of search results
- `total`: number of total matches
"""

    spec_path.write_text(content)
    return spec_path
