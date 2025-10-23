---
id: spec-feature-001
type: feature
status: completed
priority: medium
created_at: 2025-10-22T00:00:00
updated_at: 2025-10-22T12:00:00
---

# Claude Code Status Bar for Active Spec Tracking

## Description
Implement a Python script that integrates with Claude Code's status bar functionality to display active specification information. The script will be automatically installed during Quaestor project initialization via the `initializing-project` skill.

When invoked, the script checks the `.quaestor/specs/active/` directory for active specifications and displays the first active spec's name along with its progress percentage in the Claude Code status bar.

Current state: No status bar integration exists. Users must manually check `.quaestor/specs/active/` to see what specifications are currently being worked on.

Desired state: The Claude Code status bar automatically shows the active spec name and progress (e.g., "spec-auth-001 (60%)") when queried, providing instant visibility into current work without context switching.

Scope includes:
- Python script that reads active spec files from `.quaestor/specs/active/`
- Progress calculation by parsing markdown checkboxes in acceptance criteria
- Status bar configuration that Claude Code can invoke on-demand
- Integration into `initializing-project` skill for automatic installation

Scope excludes:
- Real-time filesystem watching (updates only on query)
- Support for multiple specs (shows first only)
- Custom status bar formatting options (fixed format)
- Status bar click interactions

## Rationale
Developers frequently lose track of which specification they're actively working on, especially when context switching between multiple projects or after breaks. Currently, checking active work requires opening file explorers or running terminal commands to inspect `.quaestor/specs/active/`.

Problem solved: Cognitive overhead and context switching required to answer "what am I working on?" This friction slows down workflow resumption and makes it harder to maintain focus on the current specification.

Business impact: Improved developer experience with Quaestor specifications, reduced context switching, faster workflow resumption, and better visibility into current work status.

If not done: Developers continue experiencing friction with spec awareness, leading to lower adoption of the specification workflow and reduced effectiveness of Quaestor's planning features.

## Dependencies
- **Requires**: None
- **Related**: spec-feature-002 (if created for multi-spec support in future)

## Risks
- **Integration risk**: Claude Code status bar API may have undocumented constraints or behavior.
  Mitigation: Test with multiple project types, review Claude Code documentation thoroughly, implement graceful error handling.

- **Performance risk**: Parsing markdown files on every query could add latency.
  Mitigation: Status bar checks are on-demand (not real-time), so occasional 50-100ms delay is acceptable. If needed, implement simple caching.

- **File system risk**: Spec files may be malformed or missing expected structure.
  Mitigation: Implement robust error handling, fallback to "No active spec" message on parse errors.

## Success Metrics
- Status bar query response time < 200ms (p95)
- Zero errors when no active specs exist
- Correctly parses progress from 100% of well-formed spec files
- Automatic installation success rate during project init = 100%
- Status bar displays within 500ms of Claude Code invocation

## Acceptance Criteria
- [x] Python script reads `.quaestor/specs/active/` directory and identifies spec files
- [x] Script parses first active spec file and extracts title/ID
- [x] Script calculates progress percentage by counting `[x]` vs `[ ]` checkboxes in Acceptance Criteria section
- [x] Status bar displays format: `"spec-id (progress%)"` or `"No active spec"` when none exist
- [x] Script handles missing directory gracefully with appropriate message
- [x] Script handles malformed spec files with error recovery
- [x] `initializing-project` skill automatically installs status bar configuration
- [x] Installation creates proper Claude Code status bar config file
- [x] Status bar updates on-demand when Claude Code queries it
- [x] Installation process is idempotent (safe to run multiple times)

## Test Scenarios

### Status bar shows active spec with progress
**Given**: `.quaestor/specs/active/spec-feature-001.md` exists with 3/5 checkboxes completed in Acceptance Criteria
**When**: Claude Code queries the status bar
**Then**: Status bar displays `"spec-feature-001 (60%)"`

### No active specs
**Given**: `.quaestor/specs/active/` directory is empty
**When**: Claude Code queries the status bar
**Then**: Status bar displays `"No active spec"`

### Multiple active specs
**Given**: `.quaestor/specs/active/` contains `spec-feature-001.md` and `spec-bugfix-002.md`
**When**: Claude Code queries the status bar
**Then**: Status bar displays first spec found (likely `spec-bugfix-002.md` alphabetically)

### Malformed spec file
**Given**: `.quaestor/specs/active/spec-feature-001.md` has invalid YAML frontmatter
**When**: Claude Code queries the status bar
**Then**: Status bar displays `"Error: Unable to parse spec"` or falls back to `"No active spec"`

### Directory does not exist
**Given**: `.quaestor/specs/active/` directory does not exist
**When**: Claude Code queries the status bar
**Then**: Status bar displays `"No active spec"` without crashing

### Automatic installation during init
**Given**: Running Quaestor `initializing-project` skill on a new project
**When**: Installation process completes
**Then**: Claude Code status bar configuration is created and status bar is functional

## Metadata
estimated_hours: 4
technical_notes: |
  - Status bar script location: `src/quaestor/scripts/status_bar.py`
  - Integration point: `src/quaestor/skills/initializing-project` (add status bar setup step)
  - Status bar config: Should be placed in `.claude/` or equivalent Claude Code config location
  - Progress calculation: Use regex or markdown parser to find `## Acceptance Criteria` section, count `[x]` and `[ ]` patterns
  - Error handling: Use try/except with logging, never crash status bar query
branch: feat/claude-code-status-bar
