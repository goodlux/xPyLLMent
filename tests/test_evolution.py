"""Test evolution module"""

import pytest
from unittest.mock import Mock, patch

from xpyllment.evolution import Individual, Population, FitnessFunction, EvolutionEngine
from xpyllment.config import Config


def test_individual_creation():
    """Test individual creation"""
    individual = Individual(
        experiment_id=1,
        name="test_arch",
        fitness_score=0.75,
        generation=1
    )
    
    assert individual.experiment_id == 1
    assert individual.name == "test_arch"
    assert individual.fitness_score == 0.75
    assert individual.generation == 1


def test_population_metrics():
    """Test population metrics calculation"""
    individuals = [
        Individual(1, "arch1", 0.8, 1),
        Individual(2, "arch2", 0.6, 1),
        Individual(3, "arch3", 0.9, 1),
    ]
    
    population = Population(individuals, generation=1)
    
    assert population.size == 3
    assert population.best_fitness == 0.9
    assert population.average_fitness == pytest.approx(0.767, rel=1e-2)
    
    top_2 = population.get_top_k(2)
    assert len(top_2) == 2
    assert top_2[0].fitness_score == 0.9
    assert top_2[1].fitness_score == 0.8


def test_fitness_function():
    """Test fitness function evaluation"""
    config = Config()
    fitness_fn = FitnessFunction(config.evolution)
    
    # Test successful experiment
    experiment_data = {
        'success': True,
        'benchmark_scores': {
            'arc_challenge': 0.2,
            'boolq': 0.4,
            'hellaswag': 0.3
        },
        'training_duration_minutes': 60,
        'gpu_hours': 1.0,
        'architecture_spec': {
            'proposed_changes': ['change1', 'change2', 'change3']
        }
    }
    
    fitness = fitness_fn.evaluate(experiment_data)
    assert 0.0 <= fitness <= 1.0
    
    # Test failed experiment
    failed_experiment = {'success': False}
    failed_fitness = fitness_fn.evaluate(failed_experiment)
    assert failed_fitness == 0.0


@patch('xpyllment.evolution.Database')
def test_evolution_engine_initialization(mock_db):
    """Test evolution engine initialization"""
    config = Config()
    mock_database = Mock()
    
    engine = EvolutionEngine(config, mock_database)
    
    assert engine.config == config.evolution
    assert engine.database == mock_database
    assert engine.current_generation == 0


@patch('xpyllment.evolution.Database')
def test_population_initialization(mock_db):
    """Test population initialization from database"""
    config = Config()
    mock_database = Mock()
    
    # Mock database response
    mock_experiments = [
        {
            'id': 1, 'name': 'arch1', 'fitness_score': 0.8, 'success': True,
            'generation': 0, 'parent_id': None, 'architecture_spec': {}, 'created_at': None
        },
        {
            'id': 2, 'name': 'arch2', 'fitness_score': 0.6, 'success': True,
            'generation': 0, 'parent_id': None, 'architecture_spec': {}, 'created_at': None
        }
    ]
    
    mock_database.get_top_experiments.return_value = mock_experiments
    
    engine = EvolutionEngine(config, mock_database)
    population = engine.initialize_population()
    
    assert population.size == 2
    assert population.generation == 0
    assert len(population.elite_individuals) > 0


if __name__ == "__main__":
    pytest.main([__file__])
