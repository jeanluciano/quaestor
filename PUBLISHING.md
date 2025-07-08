# Publishing Quaestor to PyPI

## First-time Setup

1. **Create a PyPI account**: https://pypi.org/account/register/
2. **Create an API token**: https://pypi.org/manage/account/token/
   - Give it a descriptive name like "quaestor-publish"
   - Copy the token (starts with `pypi-`)

3. **Set up credentials** (choose one method):

   ### Option A: Using .pypirc (local)
   ```bash
   cp .pypirc.example ~/.pypirc
   chmod 600 ~/.pypirc
   # Edit ~/.pypirc and replace YOUR_API_TOKEN_HERE with your token
   ```

   ### Option B: Using environment variables (recommended for CI)
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
   ```

## Publishing

### Manual Publishing
```bash
# Build the package
uv build

# Upload to TestPyPI first (optional but recommended)
uv run twine upload --repository testpypi dist/*

# Test from TestPyPI
uvx --index-url https://test.pypi.org/simple/ quaestor --help

# Upload to PyPI
uv run twine upload dist/*
```

### Automated Publishing (GitHub Actions)
The project includes a GitHub Action that automatically publishes to PyPI when you create a new release:

1. Go to Settings → Secrets → Actions
2. Add a secret named `PYPI_API_TOKEN` with your PyPI token
3. Create a new release on GitHub
4. The action will automatically build and publish

## Version Management

Before publishing a new version:
1. Update version in `pyproject.toml`
2. Update CHANGELOG (if you have one)
3. Commit changes
4. Create a git tag: `git tag v0.1.0`
5. Push tags: `git push --tags`