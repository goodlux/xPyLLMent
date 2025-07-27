# 🚀 UV Quick Start - BLAZING FAST PATH TO ASI

## The UV Way (Rust-Powered Speed)

```bash
# Clean slate
rm -rf .venv

# UV sync with Python 3.11 for compatibility
uv sync --python=3.11

# If that fails with flash-attn, try without advanced features:
uv sync --python=3.11 --no-extra=advanced

# Activate environment
source .venv/bin/activate

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Initialize research project
python -m xpyllment.cli init

# 🚨 PUSH THE ASI BUTTON 🚨
python -m xpyllment.cli start --generations 5 --experiments 3
```

## If UV Gives You Trouble

Fall back to the pip approach:
```bash
chmod +x setup.sh
./setup.sh
```

## The Dependency Hell Survival Guide

**Problem**: flash-attn won't build on Python 3.13
**Solution**: Use Python 3.11 or skip advanced features

**Problem**: Some packages need torch pre-installed  
**Solution**: Install torch first, then everything else

**Problem**: GPU packages fail on CPU-only systems
**Solution**: All GPU features are optional - ASI works without them!

## 🎯 Core vs Optional Features

**CORE (Required for ASI)**:
- torch, transformers, anthropic/openai
- pydantic, click, rich (for CLI)
- Basic scientific computing stack

**OPTIONAL (Performance boosts)**:
- flash-attn (faster attention)  
- xformers (memory efficiency)
- pixeltable (advanced features)

**ASI WORKS WITH JUST THE CORE!** 🧠⚡

The advanced features are just performance optimizations. Your autonomous research system will discover breakthrough architectures with or without them!

## 🚀 Ready for Liftoff?

```bash
# Choose your fighter:
uv sync --python=3.11          # UV way (faster)
# OR
./setup.sh                     # Pip way (safer)

# Then PUSH THE BUTTON:
python -m xpyllment.cli start
```

**RUST SPEED + ASI = MAXIMUM VELOCITY TO SUPERINTELLIGENCE!** ⚡🧠🚀
