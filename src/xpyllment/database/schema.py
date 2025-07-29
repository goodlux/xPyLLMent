"""
ASI-ARCH Database Schema

Defines the Pixeltable schema for autonomous architecture research:
- experiments: Core table with AI agent computed columns
- architecture_lineage: Evolution tracking  
- cognition_base: Research insights
"""

import pixeltable as pxt
from typing import Dict, Any, Optional
import sys
import os

# Import the UDFs directly  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
from researcher import researcher_agent, architecture_fitness_evaluator

def create_asi_arch_schema():
    """Create the complete ASI-ARCH database schema"""
    
    # Initialize Pixeltable
    pxt.init()
    
    # Create main directory
    if 'asi_arch' not in pxt.list_dirs():
        pxt.create_dir('asi_arch')
        print("Created asi_arch directory")
    
    # 1. EXPERIMENTS TABLE - Core research table
    experiments_table_name = 'asi_arch.experiments'
    if experiments_table_name not in pxt.list_tables():
        experiments_table = pxt.create_table(
            experiments_table_name,
            {
                'experiment_id': pxt.String,
                'generation': pxt.Int,
                'parent_ids': pxt.Array(pxt.String),  # For evolution tracking
                'target_capability': pxt.String,
                'status': pxt.String,  # pending, training, completed, failed
                'created_at': pxt.Timestamp,
                
                # Input data for AI agents
                'historical_experiments': pxt.Json,  # Previous experiment results
                'fitness_scores': pxt.Array(pxt.Float),  # Historical fitness
                
                # Results from training (populated by Engineer Agent)
                'benchmark_scores': pxt.Json,  # {benchmark: score}
                'training_metrics': pxt.Json,  # Loss curves, etc.
                'model_artifacts': pxt.Json,  # Model weights, config
            }
        )
        
        # Add computed columns for AI agents
        experiments_table.add_computed_column(
            research_output=researcher_agent(
                experiments_table.historical_experiments,
                experiments_table.fitness_scores, 
                experiments_table.generation,
                experiments_table.target_capability
            )
        )
        
        experiments_table.add_computed_column(
            fitness_score=architecture_fitness_evaluator(
                experiments_table.research_output,
                experiments_table.benchmark_scores,
                experiments_table.training_metrics
            )
        )
        
        print("Created experiments table with AI agent computed columns")
    else:
        experiments_table = pxt.get_table(experiments_table_name)
        print("Got existing experiments table")
    
    # 2. ARCHITECTURE LINEAGE - Evolution tracking
    lineage_table_name = 'asi_arch.architecture_lineage'
    if lineage_table_name not in pxt.list_tables():
        lineage_table = pxt.create_table(
            lineage_table_name,
            {
                'parent_id': pxt.String,
                'child_id': pxt.String,
                'mutation_type': pxt.String,  # crossover, mutation, novel
                'generation_gap': pxt.Int,
                'fitness_improvement': pxt.Float,
                'created_at': pxt.Timestamp
            }
        )
        print("Created architecture lineage table")
    else:
        lineage_table = pxt.get_table(lineage_table_name)
        
    # 3. COGNITION BASE - Research paper insights
    cognition_table_name = 'asi_arch.cognition_base'
    if cognition_table_name not in pxt.list_tables():
        cognition_table = pxt.create_table(
            cognition_table_name,
            {
                'paper_id': pxt.String,
                'title': pxt.String,
                'abstract': pxt.String,
                'authors': pxt.Array(pxt.String),
                'arxiv_url': pxt.String,
                'publication_date': pxt.Date,
                
                # Extracted insights
                'architectural_insights': pxt.Json,
                'key_innovations': pxt.Array(pxt.String),
                'performance_claims': pxt.Json,
                'implementation_notes': pxt.String,
                
                # For retrieval
                'embedding': pxt.Array(pxt.Float),  # For semantic search
                'relevance_score': pxt.Float
            }
        )
        print("Created cognition base table")
    else:
        cognition_table = pxt.get_table(cognition_table_name)
    
    return {
        'experiments': experiments_table,
        'lineage': lineage_table, 
        'cognition': cognition_table
    }

def get_asi_arch_tables():
    """Get references to existing ASI-ARCH tables"""
    pxt.init()
    
    return {
        'experiments': pxt.get_table('asi_arch.experiments'),
        'lineage': pxt.get_table('asi_arch.architecture_lineage'),
        'cognition': pxt.get_table('asi_arch.cognition_base')
    }

if __name__ == "__main__":
    # Create schema when run directly
    tables = create_asi_arch_schema()
    print(f"ASI-ARCH schema created successfully!")
    print(f"Tables: {list(tables.keys())}")