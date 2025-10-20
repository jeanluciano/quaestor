# JavaScript/TypeScript Quality Standards

**Load this file when:** Implementing features in JavaScript or TypeScript projects

## Validation Commands

**JavaScript:**
```bash
# Linting
npx eslint . --fix

# Formatting
npx prettier --write .

# Tests
npm test

# Full Validation Pipeline
npx eslint . && npx prettier --check . && npm test
```

**TypeScript:**
```bash
# Linting
npx eslint . --fix

# Formatting
npx prettier --write .

# Type Checking
npx tsc --noEmit

# Tests
npm test

# Full Validation Pipeline
npx eslint . && npx prettier --check . && npx tsc --noEmit && npm test
```

## Required Standards

```yaml
Code Style:
  - Line length: 100-120 characters
  - Semicolons: Consistent (prefer with)
  - Quotes: Single or double (consistent)
  - Trailing commas: Always in multiline

Testing:
  - Framework: Jest, Mocha, or Vitest
  - Coverage: >= 80%
  - Test files: *.test.js, *.spec.js
  - Mocking: Prefer dependency injection
  - Async: Use async/await, not callbacks

Documentation:
  - JSDoc for all exported functions
  - README for packages
  - Type definitions (TypeScript or JSDoc)
  - API documentation for libraries

TypeScript Specific:
  - Strict mode enabled
  - No 'any' types (use 'unknown' if needed)
  - Proper interface/type definitions
  - Generic types where appropriate
  - Discriminated unions for state

Error Handling:
  - Try/catch for async operations
  - Error boundaries (React)
  - Proper promise handling
  - No unhandled promise rejections
```

## Quality Checklist

**Before Declaring Complete:**
- [ ] No linting errors (`eslint .`)
- [ ] Code formatted (`prettier --check .`)
- [ ] Type checking passes (TS: `tsc --noEmit`)
- [ ] All tests pass (`npm test`)
- [ ] Test coverage >= 80%
- [ ] No 'any' types (TypeScript)
- [ ] All exported functions have JSDoc
- [ ] Async operations properly handled
- [ ] Error boundaries implemented (React)
- [ ] No console.log in production code

## Example Quality Pattern

**TypeScript:**
```typescript
/**
 * Load configuration from YAML file.
 *
 * @param configPath - Path to configuration file
 * @returns Parsed configuration object
 * @throws {Error} If file doesn't exist or YAML is invalid
 *
 * @example
 * ```ts
 * const config = await loadConfig('./config.yaml');
 * console.log(config.apiKey);
 * ```
 */
export async function loadConfig(configPath: string): Promise<Config> {
  if (!fs.existsSync(configPath)) {
    throw new Error(`Config not found: ${configPath}`);
  }

  try {
    const contents = await fs.promises.readFile(configPath, 'utf-8');
    const config = yaml.parse(contents) as Config;
    return config;
  } catch (error) {
    throw new Error(`Invalid YAML in ${configPath}: ${error.message}`);
  }
}
```

**JavaScript with JSDoc:**
```javascript
/**
 * @typedef {Object} Config
 * @property {string} apiKey - API key for service
 * @property {number} timeout - Request timeout in ms
 */

/**
 * Load configuration from YAML file.
 *
 * @param {string} configPath - Path to configuration file
 * @returns {Promise<Config>} Parsed configuration object
 * @throws {Error} If file doesn't exist or YAML is invalid
 */
export async function loadConfig(configPath) {
  if (!fs.existsSync(configPath)) {
    throw new Error(`Config not found: ${configPath}`);
  }

  try {
    const contents = await fs.promises.readFile(configPath, 'utf-8');
    const config = yaml.parse(contents);
    return config;
  } catch (error) {
    throw new Error(`Invalid YAML in ${configPath}: ${error.message}`);
  }
}
```

---

*JavaScript/TypeScript-specific quality standards for production-ready code*
