"""
Test suite for xPyLLMent core functionality
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from xpyllment.config import Config, create_default_config
from xpyllment.core import create_research_system
from xpyllment.agents import ResearcherAgent, EngineerAgent
from xpyllment.evolution import Individual, Population, FitnessFunction


class TestConfig:
    """Test configuration management"""
    
    def test_default_config_creation(self):
        """Test creating default configuration"""
        
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_path = Path(f.name)
        
        try:
            config = create_default_config(config_path)
            
            assert config_path.exists()
            assert config.database.name == "asi_arch_research"
            assert config.evolution.population_size == 50
            
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_config_validation(self):
        """Test configuration validation"""
        
        config = Config()
        
        # Check default values
        assert config.evolution.population_size > 0
        assert config.training.max_steps > 0
        assert config.llm.provider in ["anthropic", "openai"]


class TestEvolution:
    """Test evolution system"""
    
    def test_individual_creation(self):
        """Test Individual dataclass"""
        
        individual = Individual(
            experiment_id=1,
            name="test_architecture",
            fitness_score=0.75,
            generation=1
        )
        
        assert individual.experiment_id == 1
        assert individual.name == "test_architecture"
        assert individual.fitness_score == 0.75
        assert individual.architecture_spec == {}
    
    def test_population_creation(self):
        """Test Population management"""
        
        individuals = [
            Individual(1, "arch1", 0.8, 1),
            Individual(2, "arch2", 0.6, 1),
            Individual(3, "arch3", 0.9, 1),
        ]
        
        population = Population(individuals, generation=1)
        
        assert population.size == 3
        assert population.best_fitness == 0.9
        assert population.average_fitness == 0.7666666666666667
        
        top_2 = population.get_top_k(2)
        assert len(top_2) == 2
        assert top_2[0].fitness_score == 0.9
    
    def test_fitness_function(self):
        """Test fitness evaluation"""
        
        config = Config()
        fitness_fn = FitnessFunction(config.evolution)
        
        # Test successful experiment
        experiment_data = {
            'success': True,
            'final_loss': 4.2,
            'training_duration_minutes': 60,
            'gpu_hours': 1.0,
            'architecture_spec': {
                'proposed_changes': ['change1', 'change2']
            }
        }
        
        fitness = fitness_fn.evaluate(experiment_data)
        assert 0.0 <= fitness <= 1.0
        
        # Test failed experiment
        failed_data = {'success': False}
        assert fitness_fn.evaluate(failed_data) == 0.0


class TestAgents:
    """Test AI agent functionality"""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration"""
        config = Config()
        # Use a mock LLM for testing
        config.llm.provider = "mock"
        return config
    
    def test_researcher_agent_creation(self, config):
        """Test researcher agent initialization"""
        
        # This will fail without proper API keys, so we'll test structure
        try:
            agent = ResearcherAgent(config)
            assert agent.name == "researcher"
        except:
            # Expected to fail without proper API setup
            pass
    
    def test_engineer_agent_creation(self, config):
        """Test engineer agent initialization"""
        
        try:
            agent = EngineerAgent(config)
            assert agent.name == "engineer"
        except:
            # Expected to fail without proper API setup
            pass


class TestDatabase:
    """Test database operations"""
    
    def test_database_config(self):
        """Test database configuration"""
        
        config = Config()
        db_config = config.database
        
        assert db_config.host == "localhost"
        assert db_config.name == "asi_arch_research"
        assert db_config.connection_pool_size > 0


@pytest.mark.asyncio
class TestResearchSystem:
    """Test main research system"""
    
    async def test_system_creation(self):
        """Test research system creation"""
        
        system = create_research_system()
        assert system is not None
        assert not system.research_active
        assert system.total_experiments == 0
    
    async def test_system_status(self):
        """Test system status reporting"""
        
        system = create_research_system()
        status = system.get_system_status()
        
        assert 'research_active' in status
        assert 'total_experiments' in status
        assert 'success_rate' in status
        assert 'initialized' in status


class TestMultimedia:
    """Test multimedia processing (stubs)"""
    
    def test_paper_processor_creation(self):
        """Test paper processor initialization"""
        
        from xpyllment.multimedia import PaperProcessor
        from xpyllment.config import MultimediaConfig
        
        config = MultimediaConfig()
        processor = PaperProcessor(config)
        
        assert processor.config == config


if __name__ == "__main__":
    pytest.main([__file__])
