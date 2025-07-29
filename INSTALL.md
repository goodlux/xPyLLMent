# ASI-ARCH Installation Guide

## Quick Start (Recommended)

### Option 1: Docker (Easiest - Works Everywhere) 🐳

```bash
# 1. Clone the repository
git clone <repository-url>
cd xPyLLMent

# 2. Set up environment variables
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 3. Start with Docker Compose
docker-compose up -d

# 4. Run commands in the container
docker exec -it asi-arch-research python -m xpyllment.interactive_cli init
docker exec -it asi-arch-research python -m xpyllment.interactive_cli discover
```

### Option 2: Native Installation (Advanced) 🛠️

**Requirements:**
- Python 3.11+
- macOS/Linux (ARM64 or x86_64)
- uv package manager

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd xPyLLMent

# 2. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create virtual environment (ARM64 for M-series Macs)
arch -arm64 uv venv --python 3.11

# 4. Install package
arch -arm64 uv pip install -e .

# 5. Run CLI
./xpyllment init --non-interactive  # Quick setup
./xpyllment init                    # Interactive (in real terminal)
```

## Usage

### Basic Commands

```bash
# Initialize system
./xpyllment init

# Start autonomous research
./xpyllment discover --target reasoning --generations 3

# Check system status
./xpyllment status

# View results
./xpyllment results --latest

# List all experiments
./xpyllment list

# Create shareable snapshot
./xpyllment snapshot "breakthrough_discovery"
```

### Interactive vs Non-Interactive

- **Interactive Mode**: Use in real terminals with TTY support
- **Non-Interactive Mode**: Use in scripts, CI/CD, or non-TTY environments

```bash
# Force non-interactive (always works)
./xpyllment init --non-interactive

# Environment auto-detection (recommended)
./xpyllment init
```

## Environment Requirements

### API Keys
```bash
# Required for AI agents
export ANTHROPIC_API_KEY="your_key_here"

# Optional for additional models
export OPENAI_API_KEY="your_key_here"
```

### System Resources
- **Memory**: 4GB+ recommended
- **Storage**: 2GB+ for research data
- **Network**: Internet connection for paper downloads and API calls

## Troubleshooting

### Common Issues

**1. Architecture Mismatch (M-series Macs)**
```
ImportError: incompatible architecture (have 'x86_64', need 'arm64')
```
**Solution**: Use `arch -arm64` prefix for all commands

**2. Interactive Prompts Hanging**
```
CLI hangs on prompts
```
**Solution**: Use `--non-interactive` flag or run in proper terminal

**3. PostgreSQL Connection Issues**
```
Connection failed to Pixeltable database
```
**Solution**: Use Docker for isolated environment

### Getting Help

1. **Check system status**: `./xpyllment status`
2. **Run diagnostics**: `python debug_detailed.py`
3. **Use Docker**: Guaranteed to work in isolated environment
4. **Check logs**: Look for error messages in terminal output

## Development Setup

For contributors and developers:

```bash
# Clone repository
git clone <repository-url>
cd xPyLLMent

# Development installation
arch -arm64 uv pip install -e ".[dev]"

# Run tests
python test_cli.py

# Build Docker image
docker build -t asi-arch .
```

## Next Steps

Once installed:

1. **Initialize**: `./xpyllment init`
2. **Explore**: `./xpyllment status` to see system capabilities
3. **Research**: `./xpyllment discover` to start autonomous discovery
4. **Share**: `./xpyllment snapshot` to create reproducible research

## Platform Support

| Platform | Native | Docker | Status |
|----------|--------|--------|--------|
| macOS ARM64 (M1/M2/M3) | ✅ | ✅ | Recommended |
| macOS x86_64 | ⚠️ | ✅ | Docker preferred |
| Linux ARM64 | ✅ | ✅ | Supported |
| Linux x86_64 | ✅ | ✅ | Supported |
| Windows | ❌ | ✅ | Docker only |

**Legend**: ✅ Supported, ⚠️ Limited support, ❌ Not supported