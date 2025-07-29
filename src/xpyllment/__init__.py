"""
xPyLLMent - ASI-ARCH Research System

Autonomous AI system for discovering neural architectures through
evolutionary research with Pixeltable integration.

Based on the ASI-ARCH paper concepts, this system enables AI to conduct
its own architectural research through a multi-agent evolutionary loop:

1. Researcher Agent: Proposes novel architectures
2. Engineer Agent: Converts proposals to executable code  
3. Training Pipeline: Executes training and evaluation
4. Analyst Agent: Analyzes results and generates insights
5. Evolution Engine: Manages population and selection

Key Features:
- Evolutionary architecture discovery
- Multi-agent AI research coordination
- Pixeltable integration for data management
- Snapshot-based reproducibility
- Multimedia research capabilities (future)
- One-command deployment

Usage:
    # Initialize new research project
    xpyllment init
    
    # Start autonomous research
    xpyllment start --generations 10 --experiments 5
    
    # Check system status
    xpyllment status
    
    # Create research snapshot
    xpyllment snapshot --name "breakthrough_discovery"

For more information, see the documentation at:
https://github.com/your-org/xpyllment
"""

# Import our working ASI-ARCH system
from .asi_arch import ASIArch, get_asi_arch, initialize_asi_arch

# Legacy imports for backward compatibility (will be implemented later)
try:
    from .core import ASIArchResearchSystem, create_research_system
    from .config import Config, load_config, create_default_config
    from .database import Database, connect_database
    from .evolution import EvolutionEngine, Individual, Population
    from .agents import (
        ResearcherAgent, 
        EngineerAgent, 
        TrainingAgent, 
        AnalystAgent,
        BaseAgent
    )
    from .training import TrainingPipeline
    from .snapshots import SnapshotManager
    from .multimedia import PaperProcessor, VisualizationGenerator, VideoGenerator
except ImportError:
    # These modules don't exist yet, but that's ok
    pass

# Version information
__version__ = "0.1.0"
__author__ = "ASI-ARCH Research Team"
__email__ = "research@asi-arch.ai"
__description__ = "Autonomous AI Architecture Discovery System"

# Main components for easy import
__all__ = [
    # Working ASI-ARCH System
    "ASIArch",
    "get_asi_arch", 
    "initialize_asi_arch",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]


def quick_start(reset_db=False):
    """
    Quick start function for interactive use
    
    Returns an initialized ASI-ARCH system ready for use.
    
    Example:
        >>> import xpyllment
        >>> system = xpyllment.quick_start()
        >>> exp_id = system.start_experiment('reasoning')
        >>> results = system.get_experiment_results(exp_id)
    """
    
    return initialize_asi_arch(reset_db=reset_db)


def version_info():
    """Return version and system information"""
    
    return {
        "version": __version__,
        "author": __author__, 
        "description": __description__,
        "python_requires": ">=3.8",
        "dependencies": [
            "pixeltable",
            "torch", 
            "transformers",
            "anthropic",
            "openai",
            "pydantic",
            "loguru",
            "click",
            "rich",
            "numpy",
            "pandas"
        ]
    }


# Convenience function for CLI access
def main():
    """Entry point for CLI - uses our interactive CLI"""
    from .interactive_cli import main as interactive_main
    interactive_main()


if __name__ == "__main__":
    main()
