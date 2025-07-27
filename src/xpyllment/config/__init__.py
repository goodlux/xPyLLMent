"""
Configuration Management for xPyLLMent

Handles all configuration through YAML files with Pydantic validation.
Supports environment variable overrides and runtime updates.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import yaml
from pydantic import BaseModel, Field, validator
from loguru import logger


class DatabaseConfig(BaseModel):
    """Pixeltable database configuration"""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="asi_arch_research", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="", description="Database password")
    connection_pool_size: int = Field(default=10, description="Connection pool size")


class LLMConfig(BaseModel):
    """LLM API configuration"""
    provider: str = Field(default="anthropic", description="LLM provider (anthropic, openai)")
    model: str = Field(default="claude-3-sonnet-20240229", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key (use env var)")
    max_tokens: int = Field(default=4000, description="Max tokens per request")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    
    @validator('api_key', pre=True, always=True)
    def get_api_key_from_env(cls, v):
        """Get API key from environment if not provided"""
        if v is None:
            if cls.__fields__['provider'].default == 'anthropic':
                return os.getenv('ANTHROPIC_API_KEY')
            elif cls.__fields__['provider'].default == 'openai':
                return os.getenv('OPENAI_API_KEY')
        return v


class TrainingConfig(BaseModel):
    """Training pipeline configuration"""
    batch_size: int = Field(default=32, description="Training batch size")
    learning_rate: float = Field(default=3e-4, description="Learning rate")
    max_steps: int = Field(default=2000, description="Maximum training steps")
    eval_steps: int = Field(default=100, description="Evaluation frequency")
    save_steps: int = Field(default=500, description="Checkpoint save frequency")
    gradient_accumulation_steps: int = Field(default=1, description="Gradient accumulation")
    warmup_steps: int = Field(default=100, description="Warmup steps")
    max_grad_norm: float = Field(default=1.0, description="Gradient clipping norm")
    device: str = Field(default="auto", description="Training device (auto, cpu, cuda)")
    mixed_precision: bool = Field(default=True, description="Use mixed precision training")
    

class EvolutionConfig(BaseModel):
    """Evolution algorithm configuration"""
    population_size: int = Field(default=50, description="Population size")
    elite_size: int = Field(default=10, description="Elite selection size")
    mutation_rate: float = Field(default=0.1, description="Mutation probability")
    crossover_rate: float = Field(default=0.3, description="Crossover probability")
    diversity_threshold: float = Field(default=0.8, description="Diversity preservation threshold")
    fitness_weights: Dict[str, float] = Field(
        default={
            "performance": 0.7,
            "efficiency": 0.2, 
            "novelty": 0.1
        },
        description="Fitness function component weights"
    )


class EvaluationConfig(BaseModel):
    """Evaluation benchmark configuration"""
    benchmarks: List[str] = Field(
        default=[
            "arc_challenge", "arc_easy", "boolq", "hellaswag", 
            "piqa", "social_iqa", "winogrande", "lambada_openai"
        ],
        description="Evaluation benchmarks to run"
    )
    few_shot_examples: int = Field(default=0, description="Few-shot examples for evaluation")
    batch_size: int = Field(default=16, description="Evaluation batch size")
    max_samples: Optional[int] = Field(default=None, description="Max samples per benchmark")


class MultimediaConfig(BaseModel):
    """Multimedia processing configuration"""
    enable_paper_processing: bool = Field(default=False, description="Enable research paper processing")
    enable_visualizations: bool = Field(default=True, description="Enable visual analytics")
    enable_video_generation: bool = Field(default=False, description="Enable video generation")
    figure_extraction: bool = Field(default=False, description="Extract figures from papers")
    max_paper_size_mb: int = Field(default=50, description="Max paper size in MB")


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration"""
    use_wandb: bool = Field(default=True, description="Use Weights & Biases logging")
    wandb_project: str = Field(default="xpyllment", description="W&B project name")
    wandb_entity: Optional[str] = Field(default=None, description="W&B entity name")
    log_level: str = Field(default="INFO", description="Logging level")
    save_artifacts: bool = Field(default=True, description="Save experiment artifacts")
    checkpoint_dir: str = Field(default="./checkpoints", description="Checkpoint directory")


class Config(BaseModel):
    """Main configuration class"""
    
    # Core components
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    evolution: EvolutionConfig = Field(default_factory=EvolutionConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    multimedia: MultimediaConfig = Field(default_factory=MultimediaConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # Global settings
    project_name: str = Field(default="ASI-ARCH Research", description="Project name")
    experiment_name: Optional[str] = Field(default=None, description="Current experiment name")
    seed: int = Field(default=42, description="Random seed")
    debug: bool = Field(default=False, description="Debug mode")
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from YAML file with environment variable overrides
    
    Args:
        config_path: Path to configuration file. If None, looks for config.yaml
        
    Returns:
        Loaded and validated configuration
    """
    
    # Default config path
    if config_path is None:
        config_path = Path("config.yaml")
    
    # Load base config
    config_data = {}
    
    if config_path.exists():
        logger.info(f"Loading configuration from {config_path}")
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    else:
        logger.info(f"Configuration file {config_path} not found, using defaults")
    
    # Create and validate config
    try:
        config = Config(**config_data)
        logger.info("Configuration loaded successfully")
        
        if config.debug:
            logger.debug(f"Configuration: {config.dict()}")
            
        return config
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def save_config(config: Config, config_path: Path = Path("config.yaml")) -> None:
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration to save
        config_path: Path to save configuration
    """
    
    logger.info(f"Saving configuration to {config_path}")
    
    # Convert to dict and save
    config_dict = config.dict()
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    logger.info("Configuration saved successfully")


def create_default_config(config_path: Path = Path("config.yaml")) -> Config:
    """
    Create a default configuration file
    
    Args:
        config_path: Path to create configuration file
        
    Returns:
        Default configuration
    """
    
    logger.info(f"Creating default configuration at {config_path}")
    
    config = Config()
    save_config(config, config_path)
    
    return config


# Export for easy imports
__all__ = [
    "Config",
    "DatabaseConfig", 
    "LLMConfig",
    "TrainingConfig",
    "EvolutionConfig", 
    "EvaluationConfig",
    "MultimediaConfig",
    "MonitoringConfig",
    "load_config",
    "save_config", 
    "create_default_config",
]
