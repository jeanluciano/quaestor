# Go Quality Standards

**Load this file when:** Implementing features in Go projects

## Validation Commands

```bash
# Linting
golangci-lint run

# Formatting
gofmt -w .
# OR
go fmt ./...

# Tests
go test ./...

# Coverage
go test -cover ./...

# Race Detection
go test -race ./...

# Full Validation Pipeline
gofmt -w . && golangci-lint run && go test ./...
```

## Required Standards

```yaml
Code Style:
  - Follow: Effective Go guidelines
  - Formatting: gofmt (automatic)
  - Naming: MixedCaps, not snake_case
  - Package names: Short, concise, lowercase

Testing:
  - Framework: Built-in testing package
  - Coverage: >= 75%
  - Test files: *_test.go
  - Table-driven tests: Prefer for multiple cases
  - Benchmarks: Include for performance-critical code

Documentation:
  - Package: Package-level doc comment
  - Exported: All exported items documented
  - Examples: Provide examples for complex APIs
  - README: Clear usage instructions

Error Handling:
  - Return errors, don't panic
  - Use errors.New or fmt.Errorf
  - Wrap errors with context (errors.Wrap)
  - Check all errors explicitly
  - No ignored errors (use _ = explicitly)
```

## Quality Checklist

**Before Declaring Complete:**
- [ ] Code formatted (`gofmt` or `go fmt`)
- [ ] No linting issues (`golangci-lint run`)
- [ ] All tests pass (`go test ./...`)
- [ ] No race conditions (`go test -race ./...`)
- [ ] Test coverage >= 75%
- [ ] All exported items documented
- [ ] All errors checked explicitly
- [ ] No panics in library code
- [ ] Proper error wrapping with context
- [ ] Resource cleanup with defer

## Example Quality Pattern

```go
package config

import (
    "fmt"
    "os"

    "gopkg.in/yaml.v3"
)

// Config represents the application configuration.
type Config struct {
    APIKey  string `yaml:"api_key"`
    Timeout int    `yaml:"timeout"`
}

// LoadConfig loads configuration from a YAML file.
//
// It returns an error if the file doesn't exist or contains invalid YAML.
//
// Example:
//
//	config, err := LoadConfig("config.yaml")
//	if err != nil {
//	    log.Fatal(err)
//	}
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read config file %s: %w", path, err)
    }

    var config Config
    if err := yaml.Unmarshal(data, &config); err != nil {
        return nil, fmt.Errorf("failed to parse YAML in %s: %w", path, err)
    }

    return &config, nil
}
```

**Table-Driven Test Example:**
```go
func TestLoadConfig(t *testing.T) {
    tests := []struct {
        name    string
        path    string
        want    *Config
        wantErr bool
    }{
        {
            name: "valid config",
            path: "testdata/valid.yaml",
            want: &Config{APIKey: "test-key", Timeout: 30},
            wantErr: false,
        },
        {
            name: "missing file",
            path: "testdata/missing.yaml",
            want: nil,
            wantErr: true,
        },
        {
            name: "invalid yaml",
            path: "testdata/invalid.yaml",
            want: nil,
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := LoadConfig(tt.path)
            if (err != nil) != tt.wantErr {
                t.Errorf("LoadConfig() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("LoadConfig() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

---

*Go-specific quality standards for production-ready code*
