# Generic Language Quality Standards

**Load this file when:** Implementing in languages without specific quality standards (PHP, Ruby, C++, C#, etc.)

## General Quality Gates

```yaml
Syntax & Structure:
  - Valid syntax (runs without parse errors)
  - Consistent indentation (2 or 4 spaces)
  - Clear variable naming
  - Functions <= 50 lines (guideline)
  - Nesting depth <= 3 levels

Testing:
  - Unit tests for core functionality
  - Integration tests for workflows
  - Edge case coverage
  - Error path testing
  - Reasonable coverage (>= 70%)

Documentation:
  - README with setup instructions
  - Function/method documentation
  - Complex algorithms explained
  - API documentation (if library)
  - Usage examples

Error Handling:
  - Proper exception/error handling
  - No swallowed errors
  - Meaningful error messages
  - Graceful failure modes
  - Resource cleanup

Code Quality:
  - No code duplication
  - Clear separation of concerns
  - Meaningful names
  - Single responsibility principle
  - No magic numbers/strings
```

## Quality Checklist

**Before Declaring Complete:**
- [ ] Code runs without errors
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Error handling in place
- [ ] No obvious code smells
- [ ] Functions reasonably sized
- [ ] Clear variable names
- [ ] No TODO comments left
- [ ] Resources properly managed
- [ ] Code reviewed for clarity

## SOLID Principles

**Apply regardless of language:**

```yaml
Single Responsibility:
  - Each class/module has one reason to change
  - Clear, focused purpose
  - Avoid "god objects"

Open/Closed:
  - Open for extension, closed for modification
  - Use interfaces/traits for extensibility
  - Avoid modifying working code

Liskov Substitution:
  - Subtypes must be substitutable for base types
  - Honor contracts in inheritance
  - Avoid breaking parent behavior

Interface Segregation:
  - Many specific interfaces > one general interface
  - Clients shouldn't depend on unused methods
  - Keep interfaces focused

Dependency Inversion:
  - Depend on abstractions, not concretions
  - High-level modules independent of low-level
  - Use dependency injection
```

## Code Smell Detection

**Watch for these issues:**

```yaml
Long Methods:
  - Threshold: > 50 lines
  - Action: Extract smaller methods
  - Tool: Refactorer agent

Deep Nesting:
  - Threshold: > 3 levels
  - Action: Flatten with early returns
  - Tool: Refactorer agent

Duplicate Code:
  - Detection: Similar code blocks
  - Action: Extract to shared function
  - Tool: Refactorer agent

Large Classes:
  - Threshold: > 300 lines
  - Action: Split responsibilities
  - Tool: Architect + Refactorer agents

Magic Numbers:
  - Detection: Unexplained constants
  - Action: Named constants
  - Tool: Implementer agent

Poor Naming:
  - Detection: Unclear variable names
  - Action: Rename to be descriptive
  - Tool: Refactorer agent
```

## Example Quality Pattern

**Pseudocode showing good practices:**

```
// Good: Clear function with single responsibility
function loadConfiguration(filePath: string): Config {
    // Early validation
    if (!fileExists(filePath)) {
        throw FileNotFoundError("Config not found: " + filePath)
    }

    try {
        // Clear steps
        content = readFile(filePath)
        config = parseYAML(content)
        validateConfig(config)
        return config
    } catch (error) {
        // Proper error context
        throw ConfigError("Failed to load config from " + filePath, error)
    }
}

// Good: Named constants instead of magic numbers
const MAX_RETRY_ATTEMPTS = 3
const TIMEOUT_MS = 5000

// Good: Early returns instead of deep nesting
function processUser(user: User): Result {
    if (!user.isActive) {
        return Result.error("User not active")
    }

    if (!user.hasPermission) {
        return Result.error("Insufficient permissions")
    }

    if (!user.isVerified) {
        return Result.error("User not verified")
    }

    // Main logic only runs if all checks pass
    return Result.success(doProcessing(user))
}
```

## Language-Specific Commands

**Find and use the standard tools for your language:**

```yaml
Python: ruff, pytest, mypy
Rust: cargo clippy, cargo test, cargo fmt
JavaScript/TypeScript: eslint, prettier, jest/vitest
Go: golangci-lint, go test, gofmt
Java: checkstyle, junit, maven/gradle
C#: dotnet format, xunit, roslyn analyzers
Ruby: rubocop, rspec, yard
PHP: phpcs, phpunit, psalm/phpstan
C++: clang-tidy, gtest, clang-format
```

---

*Generic quality standards applicable across programming languages*
