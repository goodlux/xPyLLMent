# ASI-ARCH Setup Notes

## Architecture Issues (M-Series Macs)

If you encounter PostgreSQL architecture errors like:
```
ImportError: no pq wrapper available.
- couldn't import psycopg 'binary' implementation: dlopen(..., but is an incompatible architecture (have 'x86_64', need 'arm64e' or 'arm64'))
```

### Solution:
```bash
# Remove old environment
rm -rf .venv

# Create ARM64 native environment  
arch -arm64 uv venv --python 3.11

# Install with native architecture
arch -arm64 uv pip install -e .

# Test CLI
./xpyllment --help
```

## Quick Start

```bash
# Initialize system with interactive setup
./xpyllment init

# Start autonomous discovery
./xpyllment discover

# Check system status
./xpyllment status

# View results
./xpyllment results
```

## Dependencies Notes

- **Pixeltable**: Core database with AI-native features
- **PostgreSQL**: Managed automatically by pixeltable-pgserver
- **No Torch**: Optional dependency, added when needed for actual training
- **uv**: Package manager for consistent environments

## Development

```bash
# Run tests
arch -arm64 uv run python test_cli.py

# Direct module access
arch -arm64 uv run python -m xpyllment.interactive_cli [command]
```