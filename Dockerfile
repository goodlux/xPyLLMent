# ASI-ARCH Docker Image
# Provides a complete, isolated environment for autonomous architecture research

FROM python:3.11-slim

LABEL maintainer="ASI-ARCH Research Team"
LABEL description="Autonomous AI Architecture Discovery System"
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIXELTABLE_CONFIG=/app/.pixeltable

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN uv pip install --system -e .

# Create pixeltable data directory
RUN mkdir -p /app/.pixeltable

# Expose port for potential web interface
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import xpyllment; print('ASI-ARCH ready')" || exit 1

# Default command
CMD ["python", "-m", "xpyllment.interactive_cli", "init", "--non-interactive"]