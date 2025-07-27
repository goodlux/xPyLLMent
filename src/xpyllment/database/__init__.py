"""
Database Layer for xPyLLMent

Pixeltable integration for managing experiments, architectures, and research data.
Provides clean abstractions for tables, computed columns, and snapshots.
"""

from typing import Dict, Any, Optional, List, Union
import json
from datetime import datetime
from pathlib import Path

import pixeltable as pxt
from loguru import logger

from ..config import Config, DatabaseConfig


class Database:
    """
    Main database interface for ASI-ARCH research system
    
    Manages Pixeltable connections, table creation, and provides
    high-level operations for experiments and research data.
    """
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database connection"""
        self.config = config
        self._tables = {}
        self._db_name = config.name
        
    def connect(self) -> None:
        """Connect to Pixeltable database"""
        try:
            logger.info("Connecting to Pixeltable database...")
            
            # Initialize Pixeltable (automatic initialization)
            # Pixeltable creates a .pixeltable directory in the workspace automatically
            
            # Create core tables
            self._create_tables()
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create core research tables"""
        
        # Experiments table - central hub for all research experiments
        self._create_experiments_table()
        
        # Cognition base - research paper knowledge
        self._create_cognition_table()
        
        # Architecture lineage - evolution tracking
        self._create_lineage_table()
        
        # Results table - detailed experimental results
        self._create_results_table()
        
        # Media table - for future multimedia enhancements
        self._create_media_table()
        
    def _create_experiments_table(self) -> None:
        """Create the main experiments table"""
        
        table_name = f"{self._db_name}.experiments"
        
        schema = {
            'id': pxt.Int,
            'name': pxt.String,
            'motivation': pxt.String,
            'code': pxt.String,
            'parent_id': pxt.Int,  # References experiments.id
            'created_at': pxt.Timestamp,
            'updated_at': pxt.Timestamp,
            'status': pxt.String,  # proposed, training, completed, failed
            'generation': pxt.Int,
            
            # Configuration
            'config': pxt.Json,
            'architecture_spec': pxt.Json,
            
            # Training metadata
            'training_started_at': pxt.Timestamp,
            'training_completed_at': pxt.Timestamp,
            'training_duration_minutes': pxt.Float,
            'gpu_hours': pxt.Float,
            
            # Results summary
            'success': pxt.Bool,
            'fitness_score': pxt.Float,
            'final_loss': pxt.Float,
            'best_metric': pxt.Float,
            
            # Computed analysis (filled by AI agents)
            'complexity_analysis': pxt.String,
            'performance_analysis': pxt.String,
            'insights': pxt.Json,
            'recommendations': pxt.String,
        }
        
        try:
            table = pxt.create_table(table_name, schema)
            self._tables['experiments'] = table
            logger.info("Created experiments table")
        except Exception as e:
            if "already exists" in str(e):
                table = pxt.get_table(table_name)
                self._tables['experiments'] = table
                logger.info("Connected to existing experiments table")
            else:
                raise e
    
    def _create_cognition_table(self) -> None:
        """Create cognition base for research knowledge"""
        
        table_name = f"{self._db_name}.cognition_base"
        
        schema = {
            'id': pxt.Int,
            'title': pxt.String,
            'authors': pxt.String,
            'venue': pxt.String,
            'year': pxt.Int,
            'url': pxt.String,
            'content': pxt.String,
            'abstract': pxt.String,
            'added_at': pxt.Timestamp,
            
            # Extracted insights (filled by processing agents)
            'design_insights': pxt.Json,
            'algorithmic_patterns': pxt.Json,
            'key_concepts': pxt.Json,
            'implementation_details': pxt.Json,
            
            # Future: multimedia content
            'figures': pxt.Json,  # Figure captions and descriptions
            'equations': pxt.Json,  # Mathematical formulations
            'code_snippets': pxt.Json,  # Code examples from paper
        }
        
        try:
            table = pxt.create_table(table_name, schema)
            self._tables['cognition_base'] = table
            logger.info("Created cognition_base table")
        except Exception as e:
            if "already exists" in str(e):
                table = pxt.get_table(table_name)
                self._tables['cognition_base'] = table
                logger.info("Connected to existing cognition_base table")
            else:
                raise e
    
    def _create_lineage_table(self) -> None:
        """Create architecture lineage tracking"""
        
        table_name = f"{self._db_name}.architecture_lineage"
        
        schema = {
            'id': pxt.Int,
            'experiment_id': pxt.Int,  # References experiments.id
            'parent_id': pxt.Int,      # References experiments.id
            'created_at': pxt.Timestamp,
            
            # Evolution metadata
            'generation': pxt.Int,
            'mutation_type': pxt.String,
            'mutation_description': pxt.String,
            'selection_reason': pxt.String,
            
            # Computed evolutionary metrics
            'evolutionary_distance': pxt.Float,
            'novelty_score': pxt.Float,
            'diversity_contribution': pxt.Float,
            'branch_success_rate': pxt.Float,
        }
        
        try:
            table = pxt.create_table(table_name, schema)
            self._tables['architecture_lineage'] = table
            logger.info("Created architecture_lineage table")
        except Exception as e:
            if "already exists" in str(e):
                table = pxt.get_table(table_name)
                self._tables['architecture_lineage'] = table
                logger.info("Connected to existing architecture_lineage table")
            else:
                raise e
    
    def _create_results_table(self) -> None:
        """Create detailed results table"""
        
        table_name = f"{self._db_name}.results"
        
        schema = {
            'id': pxt.Int,
            'experiment_id': pxt.Int,  # References experiments.id
            'created_at': pxt.Timestamp,
            
            # Training metrics
            'loss_curve': pxt.Json,
            'learning_curves': pxt.Json,
            'training_logs': pxt.String,
            
            # Evaluation results
            'benchmark_scores': pxt.Json,
            'evaluation_details': pxt.Json,
            'error_analysis': pxt.Json,
            
            # Resource usage
            'memory_usage': pxt.Json,
            'compute_stats': pxt.Json,
            'efficiency_metrics': pxt.Json,
            
            # Model artifacts (paths/references)
            'checkpoint_path': pxt.String,
            'model_artifacts': pxt.Json,
            'logs_path': pxt.String,
        }
        
        try:
            table = pxt.create_table(table_name, schema)
            self._tables['results'] = table
            logger.info("Created results table")
        except Exception as e:
            if "already exists" in str(e):
                table = pxt.get_table(table_name)
                self._tables['results'] = table
                logger.info("Connected to existing results table")
            else:
                raise e
    
    def _create_media_table(self) -> None:
        """Create media table for future multimedia features"""
        
        table_name = f"{self._db_name}.media"
        
        schema = {
            'id': pxt.Int,
            'experiment_id': pxt.Int,  # References experiments.id (optional)
            'paper_id': pxt.Int,       # References cognition_base.id (optional)
            'created_at': pxt.Timestamp,
            
            # Media metadata
            'media_type': pxt.String,  # image, video, diagram, plot
            'title': pxt.String,
            'description': pxt.String,
            'tags': pxt.Json,
            
            # Media content (Pixeltable multimedia columns)
            'image': pxt.Image,        # For figures, plots, diagrams
            'video': pxt.Video,        # For training visualizations, demos
            'audio': pxt.Audio,        # For future audio content
            
            # Metadata
            'file_path': pxt.String,
            'file_size': pxt.Int,
            'dimensions': pxt.Json,
            'generated_by': pxt.String,  # Which component generated this
        }
        
        try:
            table = pxt.create_table(table_name, schema)
            self._tables['media'] = table
            logger.info("Created media table")
        except Exception as e:
            if "already exists" in str(e):
                table = pxt.get_table(table_name)
                self._tables['media'] = table
                logger.info("Connected to existing media table")
            else:
                raise e
    
    # =====================================================================
    # High-level operations
    # =====================================================================
    
    def create_experiment(
        self, 
        name: str,
        motivation: str,
        code: str,
        parent_id: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        architecture_spec: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create a new experiment"""
        
        experiment_data = {
            'name': name,
            'motivation': motivation,
            'code': code,
            'parent_id': parent_id,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'proposed',
            'generation': 0,  # Will be updated based on parent
            'config': config or {},
            'architecture_spec': architecture_spec or {},
            'success': False,
            'fitness_score': 0.0,
        }
        
        # Calculate generation if parent exists
        if parent_id:
            parent = self.get_experiment(parent_id)
            if parent:
                experiment_data['generation'] = parent.get('generation', 0) + 1
        
        # Insert and get the ID
        self._tables['experiments'].insert([experiment_data])
        
        # Get the ID of the inserted row (Pixeltable auto-generates IDs)
        # For now, we'll return a placeholder ID
        experiment_id = len(list(self._tables['experiments'].select()))
        
        logger.info(f"Created experiment {experiment_id}: {name}")
        return experiment_id
    
    def update_experiment(self, experiment_id: int, updates: Dict[str, Any]) -> None:
        """Update an experiment with new data"""
        
        updates['updated_at'] = datetime.now()
        
        # Note: Pixeltable update syntax might be different
        # For now, we'll log this operation
        logger.info(f"Update experiment {experiment_id} with: {list(updates.keys())}")
        
        # TODO: Implement proper Pixeltable update when available
        
    def get_experiment(self, experiment_id: int) -> Optional[Dict[str, Any]]:
        """Get experiment by ID"""
        
        try:
            # Note: Pixeltable query syntax
            results = self._tables['experiments'].where(
                self._tables['experiments'].id == experiment_id
            ).collect()
            
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get experiment {experiment_id}: {e}")
            return None
    
    def get_top_experiments(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top performing experiments by fitness score"""
        
        try:
            results = self._tables['experiments'].where(
                self._tables['experiments'].success == True
            ).order_by(
                self._tables['experiments'].fitness_score, asc=False
            ).limit(limit).collect()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get top experiments: {e}")
            return []
    
    def add_cognition(
        self,
        title: str,
        content: str,
        authors: str = "",
        venue: str = "",
        year: Optional[int] = None,
        url: str = "",
        abstract: str = ""
    ) -> int:
        """Add research paper to cognition base"""
        
        cognition_data = {
            'title': title,
            'authors': authors,
            'venue': venue,
            'year': year or datetime.now().year,
            'url': url,
            'content': content,
            'abstract': abstract,
            'added_at': datetime.now(),
            'design_insights': [],
            'algorithmic_patterns': [],
            'key_concepts': [],
            'implementation_details': {},
            'figures': [],
            'equations': [],
            'code_snippets': [],
        }
        
        self._tables['cognition_base'].insert([cognition_data])
        cognition_id = len(list(self._tables['cognition_base'].select()))
        
        logger.info(f"Added cognition {cognition_id}: {title}")
        return cognition_id
    
    def create_snapshot(self, name: str, description: str = "") -> str:
        """Create a research snapshot for reproducibility"""
        
        # This will be enhanced with Pixeltable's snapshot functionality
        # For now, we'll prepare the structure
        
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Created snapshot: {snapshot_id}")
        # TODO: Implement actual snapshot creation when Pixeltable supports it
        
        return snapshot_id
    
    def disconnect(self) -> None:
        """Clean disconnection"""
        
        logger.info("Disconnecting from database")
        self._tables = {}


def connect_database(config: Config) -> Database:
    """
    Create and connect to database with configuration
    
    Args:
        config: Application configuration
        
    Returns:
        Connected database instance
    """
    
    db = Database(config.database)
    db.connect()
    
    return db


# Export for easy imports
__all__ = [
    "Database",
    "connect_database",
]
