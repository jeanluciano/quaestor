# Rust Quality Standards

**Load this file when:** Implementing features in Rust projects

## Validation Commands

```bash
# Linting
cargo clippy -- -D warnings

# Formatting
cargo fmt

# Tests
cargo test

# Type Checking (implicit)
cargo check

# Documentation
cargo doc --no-deps --open

# Full Validation Pipeline
cargo clippy -- -D warnings && cargo fmt --check && cargo test
```

## Required Standards

```yaml
Code Style:
  - Follow: Rust API guidelines
  - Formatting: rustfmt (automatic)
  - Naming: snake_case for functions, PascalCase for types
  - Modules: Clear separation of concerns

Testing:
  - Framework: Built-in test framework
  - Coverage: >= 75%
  - Unit tests: In same file with #[cfg(test)]
  - Integration tests: In tests/ directory
  - Doc tests: In documentation examples

Documentation:
  - All public items: /// documentation
  - Modules: //! module-level docs
  - Examples: Working examples in docs
  - Safety: Document unsafe blocks thoroughly

Error Handling:
  - Use Result<T, E> for fallible operations
  - Use Option<T> for optional values
  - No .unwrap() in production code
  - Custom error types with thiserror or anyhow
  - Proper error context with context/wrap_err
```

## Quality Checklist

**Before Declaring Complete:**
- [ ] No clippy warnings (`cargo clippy -- -D warnings`)
- [ ] Code formatted (`cargo fmt --check`)
- [ ] All tests pass (`cargo test`)
- [ ] No unwrap() calls in production code
- [ ] Result<T, E> used for all fallible operations
- [ ] All public items documented
- [ ] Examples in documentation tested
- [ ] Unsafe blocks documented with safety comments
- [ ] Proper error types defined
- [ ] Resource cleanup handled (Drop trait if needed)

## Example Quality Pattern

```rust
use thiserror::Error;
use std::path::Path;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Config file not found: {0}")]
    NotFound(String),
    #[error("Invalid YAML: {0}")]
    InvalidYaml(#[from] serde_yaml::Error),
}

/// Load configuration from YAML file.
///
/// # Arguments
///
/// * `path` - Path to configuration file
///
/// # Returns
///
/// Returns the parsed configuration or an error.
///
/// # Errors
///
/// Returns `ConfigError::NotFound` if file doesn't exist.
/// Returns `ConfigError::InvalidYaml` if parsing fails.
///
/// # Examples
///
/// ```
/// let config = load_config(Path::new("config.yaml"))?;
/// ```
pub fn load_config(path: &Path) -> Result<Config, ConfigError> {
    if !path.exists() {
        return Err(ConfigError::NotFound(path.display().to_string()));
    }

    let contents = std::fs::read_to_string(path)
        .map_err(|e| ConfigError::InvalidYaml(e.into()))?;

    let config: Config = serde_yaml::from_str(&contents)?;
    Ok(config)
}
```

---

*Rust-specific quality standards for production-ready code*
