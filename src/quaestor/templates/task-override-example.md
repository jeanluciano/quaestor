---
allowed-tools: all
description: Project-specific task implementation with custom rules
---

# TASK COMMAND - PROJECT OVERRIDE
<!-- META:command:task -->
<!-- META:version:1.0-custom -->
<!-- META:project-override:true -->

## ⚡ PROJECT-SPECIFIC TASK EXECUTION ⚡

**TASK ASSIGNMENT:** $ARGUMENTS

This is a custom override for the task command specific to this project.

## 🏗️ PROJECT ARCHITECTURE AWARENESS

Before starting ANY task:
1. Review our specific architecture patterns in `.quaestor/ARCHITECTURE.md`
2. Check our coding standards in `docs/CODING_STANDARDS.md`
3. Verify component ownership in `.github/CODEOWNERS`

## 📋 CUSTOM WORKFLOW FOR THIS PROJECT

### 1. DOMAIN ANALYSIS (Mandatory)
- Identify which domain/module this task affects
- Check domain-specific rules and patterns
- Verify with domain owner if needed

### 2. IMPACT ASSESSMENT
- List all affected components
- Check for downstream dependencies
- Identify required integration tests

### 3. IMPLEMENTATION
- Follow our specific design patterns
- Use our custom utility libraries
- Apply project-specific validations

## 🎯 PROJECT-SPECIFIC QUALITY GATES

### Code Standards:
- [ ] Follows our custom ESLint configuration
- [ ] Uses our TypeScript strict settings
- [ ] Implements proper error handling with our ErrorBoundary
- [ ] Includes performance monitoring hooks

### Testing Requirements:
- [ ] Unit tests with >90% coverage
- [ ] Integration tests for API changes
- [ ] E2E tests for user-facing features
- [ ] Performance benchmarks for critical paths

### Documentation:
- [ ] API documentation in OpenAPI format
- [ ] Component documentation with examples
- [ ] Decision records for architectural changes

## 🚀 DEPLOYMENT READINESS

Before marking complete:
1. Run `npm run check:all`
2. Verify feature flags are configured
3. Update deployment documentation
4. Create rollback plan

**FINAL RESPONSE:** "Task complete. All project-specific requirements met. Ready for review."