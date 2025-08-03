---
extends: review
additional-features: ["auto-archiving", "memory-update", "specification-completion"]
---

# /review - Enhanced with Memory Management

## Additional Features

### Automatic Specification Archiving 📁

When the review process completes successfully and a PR is created, the system will:

1. **Detect Completed Specifications**
   - Analyze review output for completion indicators
   - Check acceptance criteria fulfillment
   - Identify specifications ready for archiving

2. **Archive to Completed Folder**
   ```yaml
   Auto-Archive Process:
     - Move spec from active/ to completed/
     - Update specification status
     - Preserve git history
     - Update manifest
   ```

3. **Update MEMORY.md**
   ```yaml
   Memory Updates:
     - Add completion entry with timestamp
     - Record key learnings
     - Update progress metrics
     - Archive implementation details
   ```

## Integration with Memory Management

### Before PR Creation
```yaml
Pre-Ship Checklist:
  - ✅ All active specifications reviewed
  - ✅ Progress documented in specifications
  - ✅ MEMORY.md reflects current state
  - ✅ Completion criteria verified
```

### After PR Creation
```yaml
Post-Ship Actions:
  - 📁 Archive completed specifications
  - 📝 Update MEMORY.md with completion
  - 📊 Generate completion metrics
  - 🔄 Prepare for next iteration
```

## Usage with Memory System

### Complete Review with Archiving
```bash
/review                    # Full review + auto-archive completed specs
/review --no-archive       # Review without archiving
/review --archive-only     # Archive completed specs without review
```

### Memory Integration
The review command now:
- Tracks which specifications are being shipped
- Archives completed work automatically
- Updates project memory with learnings
- Maintains specification lifecycle

## Completion Detection

### Automatic Detection
The system detects completion through:
```yaml
Indicators:
  - PR description mentions specification IDs
  - Acceptance criteria are referenced as complete
  - Commit messages indicate feature completion
  - Review output shows all tests passing
```

### Manual Override
```yaml
Force Completion:
  /review --complete spec-id-001,spec-id-002
  
Skip Completion:
  /review --no-complete
```

## Memory Update Template

When specifications are archived, MEMORY.md is updated with:

```markdown
### [Date] - Specification Completed: [spec-id]

**Completed**: [specification title]
**Duration**: [start date] to [end date]
**Key Achievements**:
- [List of completed acceptance criteria]

**Learnings**:
- [Technical decisions made]
- [Challenges overcome]
- [Patterns established]

**Metrics**:
- Lines of code: [count]
- Test coverage: [percentage]
- Performance impact: [metrics]
```

## Workflow Integration

### Standard Flow
```
/plan → /implement → /test → /review → [Auto-Archive]
                                    ↓
                              Completed specs moved
                              Memory updated
                              Ready for next cycle
```

### With Active Limit
```yaml
Active Limit Check:
  - If at limit (3 active specs)
  - Review will complete at least one
  - Enables activation of new specs
```

## Success Criteria (Enhanced)

Original criteria plus:
- ✅ Completed specifications auto-archived
- ✅ MEMORY.md updated with completion data
- ✅ Specification folders properly organized
- ✅ Git history preserved through moves
- ✅ Ready for next specification cycle

---
*Review command enhanced with automatic specification archiving and memory management*