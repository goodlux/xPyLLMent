"""Test configuration module"""

import pytest
from pathlib import Path
import tempfile
import yaml

from xpyllment.config import Config, load_config, create_default_config


def test_default_config():
    """Test default configuration creation"""
    config = Config()
    
    assert config.database.name == "asi_arch_research"
    assert config.llm.provider == "anthropic"
    assert config.training.batch_size == 32
    assert config.evolution.population_size == 50


def test_config_validation():
    """Test configuration validation"""
    # Valid config should pass
    config = Config(
        database={'name': 'test_db'},
        llm={'provider': 'anthropic', 'model': 'claude-3-sonnet-20240229'}
    )
    
    assert config.database.name == 'test_db'
    assert config.llm.provider == 'anthropic'


def test_load_config_from_file():
    """Test loading configuration from YAML file"""
    
    # Create temporary config file
    config_data = {
        'database': {'name': 'test_research_db'},
        'llm': {'provider': 'anthropic', 'temperature': 0.5},
        'training': {'batch_size': 64}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        config = load_config(config_path)
        
        assert config.database.name == 'test_research_db'
        assert config.llm.temperature == 0.5
        assert config.training.batch_size == 64
        
    finally:
        config_path.unlink()


def test_create_default_config_file():
    """Test creating default configuration file"""
    
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        config_path = Path(f.name)
    
    config_path.unlink()  # Remove the file so we can test creation
    
    try:
        config = create_default_config(config_path)
        
        assert config_path.exists()
        assert isinstance(config, Config)
        
        # Load the created file
        loaded_config = load_config(config_path)
        assert loaded_config.database.name == config.database.name
        
    finally:
        if config_path.exists():
            config_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
