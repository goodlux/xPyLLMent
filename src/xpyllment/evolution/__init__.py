"""
Evolution System for xPyLLMent

Implements evolutionary algorithms for neural architecture discovery.
Handles fitness evaluation, parent selection, and population management.
"""

from typing import Dict, Any, List, Optional, Tuple
import random
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

from loguru import logger

from ..config import Config, EvolutionConfig
from ..database import Database


@dataclass
class Individual:
    """Represents an individual in the evolution population"""
    
    experiment_id: int
    name: str
    fitness_score: float
    generation: int
    parent_id: Optional[int] = None
    architecture_spec: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.architecture_spec is None:
            self.architecture_spec = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass 
class Population:
    """Represents a population of architectures"""
    
    individuals: List[Individual]
    generation: int
    elite_individuals: List[Individual] = None
    diversity_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.elite_individuals is None:
            self.elite_individuals = []
        if self.diversity_metrics is None:
            self.diversity_metrics = {}
    
    @property
    def size(self) -> int:
        return len(self.individuals)
    
    @property
    def best_fitness(self) -> float:
        return max(ind.fitness_score for ind in self.individuals) if self.individuals else 0.0
    
    @property
    def average_fitness(self) -> float:
        return sum(ind.fitness_score for ind in self.individuals) / len(self.individuals) if self.individuals else 0.0
    
    def get_top_k(self, k: int) -> List[Individual]:
        """Get top k individuals by fitness"""
        return sorted(self.individuals, key=lambda x: x.fitness_score, reverse=True)[:k]


class FitnessFunction:
    """
    Composite fitness function for neural architectures
    
    Combines multiple objectives:
    - Performance (accuracy on benchmarks)
    - Efficiency (training time, memory usage)
    - Novelty (architectural innovation)
    """
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.weights = config.fitness_weights
        
    def evaluate(self, experiment_data: Dict[str, Any]) -> float:
        """
        Evaluate fitness of an experiment
        
        Args:
            experiment_data: Complete experiment data from database
            
        Returns:
            Fitness score between 0 and 1
        """
        
        if not experiment_data.get('success', False):
            return 0.0
        
        # Performance component
        performance_score = self._evaluate_performance(experiment_data)
        
        # Efficiency component  
        efficiency_score = self._evaluate_efficiency(experiment_data)
        
        # Novelty component
        novelty_score = self._evaluate_novelty(experiment_data)
        
        # Weighted combination
        fitness = (
            self.weights['performance'] * performance_score +
            self.weights['efficiency'] * efficiency_score + 
            self.weights['novelty'] * novelty_score
        )
        
        return max(0.0, min(1.0, fitness))
    
    def _evaluate_performance(self, experiment_data: Dict[str, Any]) -> float:
        """Evaluate performance on benchmarks"""
        
        benchmark_scores = experiment_data.get('benchmark_scores', {})
        if not benchmark_scores:
            # Fallback to loss-based performance
            final_loss = experiment_data.get('final_loss', 10.0)
            baseline_loss = 4.6  # DeltaNet baseline
            return max(0.0, (baseline_loss - final_loss) / baseline_loss)
        
        # Average benchmark performance
        scores = list(benchmark_scores.values())
        return sum(scores) / len(scores) if scores else 0.0
    
    def _evaluate_efficiency(self, experiment_data: Dict[str, Any]) -> float:
        """Evaluate training efficiency"""
        
        training_time = experiment_data.get('training_duration_minutes', 120)
        gpu_hours = experiment_data.get('gpu_hours', 2.0)
        
        # Normalize efficiency (lower is better, so invert)
        time_score = max(0.0, 1.0 - (training_time / 120.0))  # 120 min baseline
        gpu_score = max(0.0, 1.0 - (gpu_hours / 2.0))         # 2 hour baseline
        
        return (time_score + gpu_score) / 2.0
    
    def _evaluate_novelty(self, experiment_data: Dict[str, Any]) -> float:
        """Evaluate architectural novelty"""
        
        # TODO: Implement semantic similarity analysis
        # For now, use a simple heuristic based on architecture spec
        
        arch_spec = experiment_data.get('architecture_spec', {})
        proposed_changes = arch_spec.get('proposed_changes', [])
        
        # More changes = potentially more novel (simple heuristic)
        novelty = min(1.0, len(proposed_changes) / 5.0)
        
        return novelty


class SelectionStrategy(ABC):
    """Abstract base class for selection strategies"""
    
    @abstractmethod
    def select_parents(self, population: Population, num_parents: int) -> List[Individual]:
        """Select parents for reproduction"""
        pass


class TournamentSelection(SelectionStrategy):
    """Tournament selection strategy"""
    
    def __init__(self, tournament_size: int = 3):
        self.tournament_size = tournament_size
    
    def select_parents(self, population: Population, num_parents: int) -> List[Individual]:
        """Select parents using tournament selection"""
        
        parents = []
        
        for _ in range(num_parents):
            # Random tournament
            tournament = random.sample(population.individuals, 
                                     min(self.tournament_size, len(population.individuals)))
            
            # Select best from tournament
            winner = max(tournament, key=lambda x: x.fitness_score)
            parents.append(winner)
        
        return parents


class EliteSelection(SelectionStrategy):
    """Elite selection strategy - always select best individuals"""
    
    def select_parents(self, population: Population, num_parents: int) -> List[Individual]:
        """Select top performers as parents"""
        
        return population.get_top_k(num_parents)


class EvolutionEngine:
    """
    Main evolution engine for architecture discovery
    
    Manages populations, selection, and the overall evolutionary process.
    """
    
    def __init__(self, config: Config, database: Database):
        self.config = config.evolution
        self.database = database
        self.fitness_function = FitnessFunction(self.config)
        
        # Selection strategies
        self.elite_selection = EliteSelection()
        self.tournament_selection = TournamentSelection()
        
        # Current state
        self.current_generation = 0
        self.population_history: List[Population] = []
        
        logger.info(f"Initialized evolution engine with population size {self.config.population_size}")
    
    def initialize_population(self) -> Population:
        """Initialize population from existing experiments"""
        
        # Get successful experiments from database
        experiments = self.database.get_top_experiments(limit=self.config.population_size * 2)
        
        individuals = []
        for exp in experiments:
            if exp.get('success', False):
                individual = Individual(
                    experiment_id=exp['id'],
                    name=exp['name'],
                    fitness_score=exp.get('fitness_score', 0.0),
                    generation=exp.get('generation', 0),
                    parent_id=exp.get('parent_id'),
                    architecture_spec=exp.get('architecture_spec', {}),
                    metadata={'created_at': exp.get('created_at')}
                )
                individuals.append(individual)
        
        # If not enough individuals, we'll need to create baseline ones
        if len(individuals) < self.config.elite_size:
            logger.warning(f"Only {len(individuals)} individuals found, need at least {self.config.elite_size}")
        
        # Sort by fitness and take top performers
        individuals.sort(key=lambda x: x.fitness_score, reverse=True)
        individuals = individuals[:self.config.population_size]
        
        population = Population(
            individuals=individuals,
            generation=self.current_generation
        )
        
        # Calculate diversity metrics
        population.diversity_metrics = self._calculate_diversity(population)
        
        # Select elite individuals
        population.elite_individuals = population.get_top_k(self.config.elite_size)
        
        logger.info(f"Initialized population with {len(individuals)} individuals")
        logger.info(f"Best fitness: {population.best_fitness:.3f}, Average: {population.average_fitness:.3f}")
        
        return population
    
    def evolve_generation(self, current_population: Population) -> List[Individual]:
        """
        Evolve one generation and return parent candidates
        
        Returns list of individuals selected as parents for new architectures
        """
        
        self.current_generation += 1
        
        logger.info(f"Evolving generation {self.current_generation}")
        logger.info(f"Current population: {current_population.size} individuals")
        logger.info(f"Best fitness: {current_population.best_fitness:.3f}")
        
        # Selection for reproduction
        num_new_offspring = max(1, self.config.population_size // 4)  # 25% new offspring per generation
        
        # Combine elite and tournament selection
        elite_parents = self.elite_selection.select_parents(
            current_population, 
            min(self.config.elite_size, num_new_offspring)
        )
        
        tournament_parents = self.tournament_selection.select_parents(
            current_population,
            max(0, num_new_offspring - len(elite_parents))
        )
        
        selected_parents = elite_parents + tournament_parents
        
        logger.info(f"Selected {len(selected_parents)} parents for reproduction")
        logger.info(f"  Elite parents: {len(elite_parents)}")
        logger.info(f"  Tournament parents: {len(tournament_parents)}")
        
        # Update population history
        self.population_history.append(current_population)
        
        return selected_parents
    
    def update_population(self, new_individuals: List[Individual]) -> Population:
        """Update population with new individuals"""
        
        # Get current population
        current_pop = self.population_history[-1] if self.population_history else Population([], 0)
        
        # Combine old and new individuals
        all_individuals = current_pop.individuals + new_individuals
        
        # Selection for survival (environmental selection)
        all_individuals.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Keep top performers + some diversity
        survivors = self._environmental_selection(all_individuals)
        
        # Create new population
        new_population = Population(
            individuals=survivors,
            generation=self.current_generation
        )
        
        # Update metrics
        new_population.diversity_metrics = self._calculate_diversity(new_population)
        new_population.elite_individuals = new_population.get_top_k(self.config.elite_size)
        
        logger.info(f"Updated population: {new_population.size} individuals")
        logger.info(f"New best fitness: {new_population.best_fitness:.3f}")
        
        return new_population
    
    def _environmental_selection(self, individuals: List[Individual]) -> List[Individual]:
        """Environmental selection to maintain population size and diversity"""
        
        if len(individuals) <= self.config.population_size:
            return individuals
        
        # Always keep elite individuals
        elite = individuals[:self.config.elite_size]
        remaining = individuals[self.config.elite_size:]
        
        # For remaining slots, balance fitness and diversity
        remaining_slots = self.config.population_size - self.config.elite_size
        
        if remaining_slots <= 0:
            return elite
        
        # Simple diversity preservation: avoid too similar architectures
        diverse_selection = []
        for candidate in remaining:
            if len(diverse_selection) < remaining_slots:
                # Check if candidate is too similar to already selected
                is_diverse = True
                for selected in elite + diverse_selection:
                    if self._similarity_score(candidate, selected) > self.config.diversity_threshold:
                        is_diverse = False
                        break
                
                if is_diverse:
                    diverse_selection.append(candidate)
        
        # Fill remaining slots with best fitness
        total_selected = len(elite) + len(diverse_selection)
        if total_selected < self.config.population_size:
            needed = self.config.population_size - total_selected
            fitness_selection = [ind for ind in remaining if ind not in diverse_selection]
            fitness_selection.sort(key=lambda x: x.fitness_score, reverse=True)
            diverse_selection.extend(fitness_selection[:needed])
        
        return elite + diverse_selection
    
    def _calculate_diversity(self, population: Population) -> Dict[str, float]:
        """Calculate diversity metrics for population"""
        
        if len(population.individuals) < 2:
            return {'average_distance': 0.0, 'diversity_index': 0.0}
        
        # Calculate pairwise similarities
        similarities = []
        individuals = population.individuals
        
        for i in range(len(individuals)):
            for j in range(i + 1, len(individuals)):
                sim = self._similarity_score(individuals[i], individuals[j])
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        diversity_index = 1.0 - avg_similarity  # Higher diversity = lower similarity
        
        return {
            'average_distance': 1.0 - avg_similarity,
            'diversity_index': diversity_index,
            'population_size': len(individuals)
        }
    
    def _similarity_score(self, ind1: Individual, ind2: Individual) -> float:
        """Calculate similarity between two individuals"""
        
        # Simple similarity based on architecture spec
        spec1 = ind1.architecture_spec
        spec2 = ind2.architecture_spec
        
        if not spec1 or not spec2:
            return 0.0
        
        # Compare proposed changes (simple Jaccard similarity)
        changes1 = set(spec1.get('proposed_changes', []))
        changes2 = set(spec2.get('proposed_changes', []))
        
        if not changes1 and not changes2:
            return 1.0
        
        intersection = len(changes1.intersection(changes2))
        union = len(changes1.union(changes2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_population_stats(self) -> Dict[str, Any]:
        """Get current population statistics"""
        
        if not self.population_history:
            return {'error': 'No population data available'}
        
        current_pop = self.population_history[-1]
        
        return {
            'generation': self.current_generation,
            'population_size': current_pop.size,
            'best_fitness': current_pop.best_fitness,
            'average_fitness': current_pop.average_fitness,
            'diversity_metrics': current_pop.diversity_metrics,
            'elite_count': len(current_pop.elite_individuals),
            'total_generations': len(self.population_history)
        }


# Export for easy imports
__all__ = [
    "Individual",
    "Population", 
    "FitnessFunction",
    "EvolutionEngine",
    "SelectionStrategy",
    "TournamentSelection",
    "EliteSelection",
]
