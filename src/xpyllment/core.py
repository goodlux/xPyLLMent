"""
Core ASI-ARCH Research System

Main orchestrator that coordinates the evolutionary research loop:
Researcher → Engineer → Training → Analyst → Evolution → Repeat
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from loguru import logger

from .config import Config, load_config
from .database import Database, connect_database
from .evolution import EvolutionEngine, Individual, Population
from .agents import ResearcherAgent, EngineerAgent, TrainingAgent, AnalystAgent
from .training import TrainingPipeline
from .snapshots import SnapshotManager


class ASIArchResearchSystem:
    """
    Main ASI-ARCH research system orchestrator
    
    Coordinates the evolutionary research loop where AI agents
    autonomously discover new neural architectures.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the research system"""
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Initialize core components
        self.database: Optional[Database] = None
        self.evolution_engine: Optional[EvolutionEngine] = None
        self.snapshot_manager: Optional[SnapshotManager] = None
        
        # Initialize AI agents
        self.researcher_agent: Optional[ResearcherAgent] = None
        self.engineer_agent: Optional[EngineerAgent] = None
        self.training_agent: Optional[TrainingAgent] = None
        self.analyst_agent: Optional[AnalystAgent] = None
        
        # Initialize training pipeline
        self.training_pipeline: Optional[TrainingPipeline] = None
        
        # System state
        self.current_population: Optional[Population] = None
        self.research_active = False
        self.total_experiments = 0
        self.successful_experiments = 0
        
        logger.info("ASI-ARCH Research System initialized")
    
    async def initialize(self) -> None:
        """Initialize all system components"""
        
        logger.info("Initializing ASI-ARCH research system...")
        
        try:
            # Connect to database
            logger.info("Connecting to database...")
            self.database = connect_database(self.config)
            
            # Initialize agents
            logger.info("Initializing AI agents...")
            self.researcher_agent = ResearcherAgent(self.config)
            self.engineer_agent = EngineerAgent(self.config)
            self.training_agent = TrainingAgent(self.config)
            self.analyst_agent = AnalystAgent(self.config)
            
            # Initialize training pipeline
            logger.info("Initializing training pipeline...")
            self.training_pipeline = TrainingPipeline(self.config)
            
            # Initialize evolution engine
            logger.info("Initializing evolution engine...")
            self.evolution_engine = EvolutionEngine(self.config, self.database)
            
            # Initialize snapshot manager
            logger.info("Initializing snapshot manager...")
            self.snapshot_manager = SnapshotManager(self.config, self.database)
            
            # Initialize population
            logger.info("Initializing research population...")
            self.current_population = self.evolution_engine.initialize_population()
            
            logger.info("ASI-ARCH research system ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize research system: {e}")
            raise
    
    async def run_research_loop(
        self, 
        max_generations: int = 10,
        experiments_per_generation: int = 5
    ) -> None:
        """
        Run the main research loop
        
        Args:
            max_generations: Maximum number of generations to evolve
            experiments_per_generation: Number of experiments per generation
        """
        
        if not self.evolution_engine or not self.current_population:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        logger.info(f"Starting research loop: {max_generations} generations, {experiments_per_generation} experiments each")
        
        self.research_active = True
        
        try:
            for generation in range(max_generations):
                if not self.research_active:
                    logger.info("Research loop stopped by user")
                    break
                
                logger.info(f"=== GENERATION {generation + 1}/{max_generations} ===")
                
                # 1. Evolution: Select parents for new architectures
                selected_parents = self.evolution_engine.evolve_generation(self.current_population)
                
                # 2. Generate new experiments
                new_individuals = await self._generate_experiments(
                    selected_parents, experiments_per_generation
                )
                
                # 3. Update population with new results
                self.current_population = self.evolution_engine.update_population(new_individuals)
                
                # 4. Create snapshot of current state
                if generation % 5 == 0:  # Snapshot every 5 generations
                    snapshot_id = self.snapshot_manager.create_snapshot(
                        f"generation_{generation + 1}",
                        f"Research state after generation {generation + 1}"
                    )
                    logger.info(f"Created snapshot: {snapshot_id}")
                
                # 5. Log progress
                stats = self.evolution_engine.get_population_stats()
                logger.info(f"Generation {generation + 1} complete:")
                logger.info(f"  Best fitness: {stats['best_fitness']:.3f}")
                logger.info(f"  Average fitness: {stats['average_fitness']:.3f}")
                logger.info(f"  Diversity index: {stats['diversity_metrics'].get('diversity_index', 0):.3f}")
                logger.info(f"  Total experiments: {self.total_experiments}")
                logger.info(f"  Successful: {self.successful_experiments}")
        
        except Exception as e:
            logger.error(f"Research loop failed: {e}")
            raise
        
        finally:
            self.research_active = False
            logger.info("Research loop completed")
    
    async def _generate_experiments(
        self, 
        parent_individuals: List[Individual], 
        num_experiments: int
    ) -> List[Individual]:
        """
        Generate and execute new experiments based on parent architectures
        
        Args:
            parent_individuals: Selected parent architectures
            num_experiments: Number of experiments to generate
            
        Returns:
            List of new individuals with results
        """
        
        new_individuals = []
        
        for i in range(num_experiments):
            try:
                logger.info(f"Generating experiment {i + 1}/{num_experiments}")
                
                # Select parent for this experiment
                parent = parent_individuals[i % len(parent_individuals)]
                
                # Generate new experiment
                individual = await self._generate_single_experiment(parent)
                
                if individual:
                    new_individuals.append(individual)
                    if individual.fitness_score > 0:
                        self.successful_experiments += 1
                
                self.total_experiments += 1
                
            except Exception as e:
                logger.error(f"Failed to generate experiment {i + 1}: {e}")
                continue
        
        return new_individuals
    
    async def _generate_single_experiment(self, parent: Individual) -> Optional[Individual]:
        """
        Generate and execute a single experiment
        
        Args:
            parent: Parent architecture to evolve from
            
        Returns:
            New individual with results or None if failed
        """
        
        try:
            # 1. RESEARCHER: Generate architecture proposal
            logger.debug("Researcher: Generating architecture proposal...")
            
            # Get historical context
            historical_experiments = self.database.get_top_experiments(limit=20)
            cognition_insights = self._get_cognition_insights()
            parent_config = parent.architecture_spec
            
            proposal_inputs = {
                'historical_experiments': historical_experiments,
                'cognition_insights': cognition_insights,
                'parent_config': parent_config
            }
            
            proposal = self.researcher_agent.process(proposal_inputs)
            
            if 'error' in proposal:
                logger.error(f"Researcher failed: {proposal['error']}")
                return None
            
            # 2. ENGINEER: Generate executable code
            logger.debug("Engineer: Generating executable code...")
            
            # Get base code from parent or default
            base_code = self._get_base_code(parent)
            
            code_inputs = {
                'architecture_spec': proposal,
                'base_code': base_code
            }
            
            code_result = self.engineer_agent.process(code_inputs)
            
            if 'error' in code_result:
                logger.error(f"Engineer failed: {code_result['error']}")
                return None
            
            # 3. Create experiment in database
            experiment_id = self.database.create_experiment(
                name=proposal['name'],
                motivation=proposal['motivation'],
                code=code_result['code'],
                parent_id=parent.experiment_id,
                architecture_spec=proposal
            )
            
            # 4. TRAINING: Execute training and evaluation
            logger.debug("Training: Executing model training...")
            
            training_results = self.training_pipeline.train_model(
                code=code_result['code'],
                experiment_name=proposal['name'],
                config_overrides={}
            )
            
            # 5. Calculate fitness score
            fitness_score = self.evolution_engine.fitness_function.evaluate(training_results)
            
            # 6. Update experiment with results
            self.database.update_experiment(experiment_id, {
                'status': 'completed',
                'success': training_results.get('success', False),
                'fitness_score': fitness_score,
                'final_loss': training_results.get('final_loss', 10.0),
                'training_duration_minutes': training_results.get('training_time', 0),
                'gpu_hours': training_results.get('gpu_hours', 0),
                'training_completed_at': datetime.now()
            })
            
            # 7. ANALYST: Generate insights (optional for now)
            # TODO: Implement analyst processing
            
            # 8. Create new individual
            new_individual = Individual(
                experiment_id=experiment_id,
                name=proposal['name'],
                fitness_score=fitness_score,
                generation=parent.generation + 1,
                parent_id=parent.experiment_id,
                architecture_spec=proposal,
                metadata={
                    'created_at': datetime.now(),
                    'success': training_results.get('success', False),
                    'training_time': training_results.get('training_time', 0)
                }
            )
            
            logger.info(f"Experiment completed: {proposal['name']} (fitness: {fitness_score:.3f})")
            
            return new_individual
            
        except Exception as e:
            logger.error(f"Failed to generate experiment: {e}")
            return None
    
    def _get_cognition_insights(self) -> Dict[str, Any]:
        """Get insights from cognition base"""
        
        # TODO: Implement cognition retrieval
        # This should query the cognition base and return relevant insights
        
        return {
            'design_insights': [
                "Linear attention mechanisms provide sub-quadratic complexity",
                "Gating mechanisms improve information flow control",
                "Hierarchical processing enhances multi-scale understanding"
            ],
            'algorithmic_patterns': [
                "Delta rule for efficient state updates",
                "Chunked processing for memory efficiency", 
                "Attention with causal masking"
            ]
        }
    
    def _get_base_code(self, parent: Individual) -> str:
        """Get base code for architecture implementation"""
        
        # Get code from parent experiment if available
        if parent.experiment_id:
            parent_experiment = self.database.get_experiment(parent.experiment_id)
            if parent_experiment and parent_experiment.get('code'):
                return parent_experiment['code']
        
        # Return default DeltaNet implementation
        return """
import torch
import torch.nn as nn
import torch.nn.functional as F

class DeltaNet(nn.Module):
    def __init__(self, d_model=256, num_heads=8, **kwargs):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        # Basic implementation - to be evolved
        
    def forward(self, x):
        # Basic forward pass - to be evolved
        return x
"""
    
    def stop_research(self) -> None:
        """Stop the research loop gracefully"""
        
        logger.info("Stopping research loop...")
        self.research_active = False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        
        status = {
            'research_active': self.research_active,
            'total_experiments': self.total_experiments,
            'successful_experiments': self.successful_experiments,
            'success_rate': self.successful_experiments / max(1, self.total_experiments),
            'initialized': all([
                self.database,
                self.evolution_engine,
                self.current_population,
                self.researcher_agent,
                self.engineer_agent,
                self.training_pipeline
            ])
        }
        
        if self.evolution_engine and self.current_population:
            status.update(self.evolution_engine.get_population_stats())
        
        return status
    
    def create_research_snapshot(self, name: str, description: str = "") -> str:
        """Create a snapshot of current research state"""
        
        if not self.snapshot_manager:
            raise RuntimeError("System not initialized")
        
        return self.snapshot_manager.create_snapshot(name, description)
    
    async def shutdown(self) -> None:
        """Clean shutdown of all components"""
        
        logger.info("Shutting down ASI-ARCH research system...")
        
        # Stop research if running
        if self.research_active:
            self.stop_research()
        
        # Disconnect database
        if self.database:
            self.database.disconnect()
        
        logger.info("Shutdown complete")


# Factory function for easy system creation
def create_research_system(config_path: Optional[Path] = None) -> ASIArchResearchSystem:
    """
    Create and return a new ASI-ARCH research system
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Initialized research system
    """
    
    return ASIArchResearchSystem(config_path)


# Export for easy imports
__all__ = [
    "ASIArchResearchSystem",
    "create_research_system",
]
