---
name: Pull Request Generator
description: Generate comprehensive PR descriptions from completed specifications and create GitHub pull requests. Use when user wants to create a PR, mentions pull request, or completes a specification.
allowed-tools: [Read, Bash]
---

# Pull Request Generator

I create well-structured pull request descriptions from completed specifications and submit them to GitHub using the `gh` CLI.

## When to Use Me

- User says: "create a pull request"
- User says: "make a PR for spec-feature-001"
- User completes a spec and asks: "what's next?"
- User mentions: "submit for review", "create pr", "pull request"

## What I Do

### 1. Read Completed Specification

I look in `.quaestor/specs/completed/` for the spec file and extract:
- Title and description
- Acceptance criteria (all should be ✅ checked)
- Test scenarios
- Technical notes
- Dependencies and risks

### 2. Generate PR Description

I create a comprehensive PR description following this template:

```markdown
## 🎯 Specification: [spec-id] - [Title]

### 📋 Summary
[High-level description from spec]

### ✅ Acceptance Criteria Met
- [x] Criterion 1: [Description]
- [x] Criterion 2: [Description]
- [x] Criterion 3: [Description]
[All criteria from spec with checkboxes marked]

### 🧪 Testing
**Test Scenarios Implemented:**
[Count]/[Total] scenarios from specification

**Test Coverage:**
[Report if available, or "See test files for details"]

**All Tests Passing:** ✅ | ❌

### 📚 Documentation
- **Specification**: `.quaestor/specs/completed/[spec-id].md`
- **Files Changed**: [List from git diff]
- **API Changes**: [If any, from spec notes]
- **Breaking Changes**: [If any, flagged prominently]

### 🔍 Technical Details
[Implementation approach and key decisions from spec technical_notes]

### 📊 Metrics
- **Files Changed**: [Count from git]
- **Lines Added/Removed**: +[X]/-[Y]
- **Estimated vs Actual**: [If time tracked]
- **Complexity**: [If noted]

### 🚀 Dependencies
[List from spec dependencies section]

### 🔗 Related
- Closes #[issue number if linked]
- Specification: [spec-id]
- Related specs: [From spec dependencies]

---
*Generated from specification: `.quaestor/specs/completed/[spec-id].md`*
```

### 3. Create GitHub PR

Using `gh` CLI, I submit the PR:

```bash
gh pr create \
  --title "[type]: [spec title]" \
  --body "[generated description]" \
  --base main
```

## Usage Examples

### Example 1: Create PR for Completed Spec

```bash
User: "create a pull request for spec-feature-001"

Me:
1. Find spec: .quaestor/specs/completed/spec-feature-001.md
2. Read content and extract details
3. Generate PR description
4. Check git status:
   - Are there uncommitted changes? → Warn user
   - Is branch ahead of main? → Good to go
5. Create PR:
   gh pr create --title "feat: User Authentication System" \
     --body "[comprehensive description]" \
     --base main
6. Report PR URL: https://github.com/user/repo/pull/123
```

### Example 2: From Spec Completion

```bash
User: "complete spec-feature-001"

Spec Management Skill:
- Moves spec to completed/
- Responds: "✅ Completed! Ready to create PR?"

User: "yes"

Me:
- Generate PR description
- Create pull request
- Report success
```

### Example 3: Batch PR Creation

```bash
User: "create PRs for all completed specs from this week"

Me:
1. Find specs in completed/ modified in last 7 days
2. For each spec:
   - Check if branch exists
   - Check if already has PR (gh pr list)
   - If no PR: create one
3. Report:
   ✅ Created PRs:
   - PR #123: spec-feature-001
   - PR #124: spec-bugfix-001
   ⏭️  Skipped (already has PR):
   - spec-feature-002
```

## PR Title Formatting

I use conventional commit format:

```
[type]: [spec title]

Examples:
- feat: User Authentication System
- fix: Memory leak in background processor
- refactor: Simplify authentication logic
- docs: API documentation update
- perf: Optimize database queries
- test: Add integration tests for auth
- security: Implement rate limiting
```

Type mapping from spec:
- `feature` → `feat:`
- `bugfix` → `fix:`
- `refactor` → `refactor:`
- `documentation` → `docs:`
- `performance` → `perf:`
- `testing` → `test:`
- `security` → `security:`

## Pr Description Sections

### Summary Section
Pulled from spec's **Description** field:
```markdown
### 📋 Summary
Implement a secure user authentication system with login, logout,
and session management capabilities. The system supports
username/password authentication with JWT tokens.
```

### Acceptance Criteria Section
All checkboxes from spec's **Acceptance Criteria**:
```markdown
### ✅ Acceptance Criteria Met
- [x] User can login with email and password
- [x] Invalid credentials show appropriate error
- [x] Sessions expire after 24 hours of inactivity
- [x] User can logout and invalidate their session
```

### Testing Section
From spec's **Test Scenarios** + git/test info:
```markdown
### 🧪 Testing
**Test Scenarios Implemented:** 4/4
- ✅ Successful login
- ✅ Invalid credentials
- ✅ Session expiry
- ✅ Logout flow

**Test Coverage:** 87% (from pytest --cov if run)
**All Tests Passing:** ✅
```

### Technical Details Section
From spec's **Metadata** and **Technical Notes**:
```markdown
### 🔍 Technical Details
**Implementation Approach:**
- Using bcrypt for password hashing
- JWT tokens with 24-hour expiry
- Redis for session storage
- Middleware for authentication checks

**Key Decisions:**
[From spec's rationale and technical_notes]
```

## Git Integration

### Pre-Flight Checks

Before creating PR, I verify:

```yaml
Checks:
  - ✅ On a feature branch (not main/master)
  - ✅ Branch is ahead of base branch
  - ✅ No uncommitted changes (git status clean)
  - ✅ Spec exists in completed/ folder
  - ✅ gh CLI is installed and configured
  - ⚠️  Tests passing (warn if not)
```

### Git Status Check

```bash
# Check current branch
git branch --show-current

# Check for uncommitted changes
git status --porcelain

# Check if ahead of main
git rev-list --count main..HEAD
```

### PR Creation Command

```bash
gh pr create \
  --title "feat: User Authentication System" \
  --body "$(cat <<'EOF'
[Full PR description here]
EOF
  )" \
  --base main \
  --head feature/user-auth
```

### Post-Creation Actions

```bash
# Get PR number
PR_NUM=$(gh pr view --json number -q .number)

# Add labels
gh pr edit $PR_NUM --add-label "specification-complete"

# Link to spec in PR
gh pr comment $PR_NUM --body "Specification: .quaestor/specs/completed/spec-feature-001.md"
```

## Error Handling

### Issue: Spec Not in Completed Folder

```
❌ Cannot create PR - spec-feature-001 not completed

Current location: .quaestor/specs/active/
Progress: 80% (4/5 criteria)

💡 Complete remaining criteria:
  - [ ] Password reset via email

Run: /impl spec-feature-001 or "complete spec-feature-001"
```

### Issue: Uncommitted Changes

```
❌ Cannot create PR - uncommitted changes detected

Uncommitted files:
  modified: src/auth/service.py
  new file: tests/test_auth.py

💡 Commit your changes first:
  git add .
  git commit -m "feat: implement user authentication"
```

### Issue: gh CLI Not Installed

```
❌ Cannot create PR - gh CLI not found

Install GitHub CLI:
  - macOS: brew install gh
  - Linux: See https://cli.github.com/
  - Windows: See https://cli.github.com/

Then authenticate:
  gh auth login
```

### Issue: Not Authenticated

```
❌ Cannot create PR - not authenticated with GitHub

Run: gh auth login

Choose authentication method:
  1. Login with web browser
  2. Login with token
```

### Issue: PR Already Exists

```
⚠️  Pull request already exists for this branch

Existing PR: #123 "feat: User Authentication System"
URL: https://github.com/user/repo/pull/123

Options:
  1. Update existing PR: (I can update the description)
  2. Create from different branch
  3. Cancel
```

## Advanced Features

### Multi-Spec PRs

If user wants to combine multiple specs:

```bash
User: "create PR for spec-feature-001 and spec-feature-002"

Me:
1. Verify both in completed/
2. Combine their descriptions
3. Merge acceptance criteria lists
4. Create single PR with both specs referenced
5. Title: "feat: User Auth + Email Notifications"
```

### Draft PRs

```bash
User: "create draft PR for spec-feature-001"

Me:
gh pr create \
  --title "feat: User Authentication System" \
  --body "[description]" \
  --draft \
  --base main

💡 Mark as ready when tests pass:
  gh pr ready [PR_NUM]
```

### PR with Reviewers

```bash
User: "create PR and request review from @alice"

Me:
gh pr create \
  --title "feat: User Authentication System" \
  --body "[description]" \
  --base main \
  --reviewer alice
```

## Integration with Commands

### With /review

```bash
User: "/review"
Review command checks code → I create PR with review notes
```

### With Spec Management

```bash
Spec Management Skill completes spec →
I'm triggered to offer PR creation →
User confirms → I generate and submit PR
```

## Tips for Best PRs

### Keep Specs Updated
Ensure completed specs have:
- ✅ All checkboxes marked [x]
- ✅ Technical notes filled in
- ✅ Test scenarios documented
- ✅ Branch linked in frontmatter

### Run Tests Before PR
```bash
# Python
pytest --cov

# JavaScript
npm test

# Rust
cargo test
```

### Review Git Diff
```bash
git diff main..HEAD

# Check what will be in PR
gh pr diff
```

### Clean Commit History
```bash
# Squash commits if messy
git rebase -i main

# Or let me create with "squash" option
User: "create PR and squash commits"
```

---

*I turn your completed specifications into polished pull requests ready for review. Just complete your spec and say "create a PR"!*
