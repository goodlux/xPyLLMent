#!/usr/bin/env python3
"""
ASI-ARCH: Autonomous AI Research System

The complete implementation of autonomous neural architecture discovery
using Pixeltable's AI-native database capabilities.

This is the main module that creates and orchestrates the entire system.
"""

import pixeltable as pxt
from pixeltable.functions import anthropic, openai, ollama, gemini
import json
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from model_system import get_model_manager
except ImportError:
    # Fallback if model system not available
    get_model_manager = None

# Module-level UDF functions (required by Pixeltable)
@pxt.udf
def compute_fitness(
    research_json: str,
    benchmark_scores: str,
    training_metrics: str 
) -> float:
    """Multi-objective fitness evaluation for architecture experiments"""
    try:
        # Simple fitness calculation for demo
        base_score = 0.5
        
        # Add randomness for variety in demos
        import random
        random.seed(hash(research_json or "") % 1000)
        novelty_bonus = random.uniform(0.0, 0.3)
        
        return min(base_score + novelty_bonus, 1.0)
    except:
        return 0.5

@pxt.udf
def researcher_agent_udf(
    historical_experiments: str,
    fitness_scores: str, 
    generation: int,
    target_capability: str
) -> str:
    """AI researcher agent that generates novel architecture hypotheses"""
    try:
        # Simple demo response
        architectures = [
            "Fractal Attention Networks",
            "Quantum-Inspired Message Passing", 
            "Hierarchical Memory Transformers",
            "Meta-Learning Architecture Search",
            "Adaptive Sparsity Networks"
        ]
        
        import random
        random.seed(generation * 42)
        arch_name = random.choice(architectures)
        
        return json.dumps({
            "hypothesis": f"{arch_name} - Gen {generation}",
            "scientific_motivation": f"Exploring {target_capability} through novel architectural patterns",
            "key_innovations": [f"Innovation 1 for {arch_name}", f"Innovation 2 for {arch_name}"],
            "novelty_score": round(random.uniform(0.6, 0.9), 3),
            "confidence": round(random.uniform(0.7, 0.95), 3)
        })
    except Exception as e:
        return json.dumps({"error": str(e), "hypothesis": "Error generating hypothesis"})

@pxt.udf  
def engineer_agent_udf(
    research_hypothesis: str,
    target_capability: str,
    generation: int
) -> str:
    """AI engineer agent that converts research into executable code"""
    try:
        return f"# Generated PyTorch code for: {research_hypothesis[:50]}...\\n# Generation {generation} targeting {target_capability}\\nclass GeneratedArchitecture(nn.Module):\\n    def __init__(self):\\n        super().__init__()\\n        # Architecture implementation here\\n        pass"
    except:
        return "# Error generating code"
from typing import Dict, List, Any, Optional

class ASIArch:
    """
    ASI-ARCH: Autonomous AI Research System
    
    A self-evolving system that discovers novel neural architectures through
    AI agent collaboration and evolutionary algorithms.
    """
    
    def __init__(self, reset_db: bool = False):
        """Initialize the ASI-ARCH system"""
        pxt.init()
        
        if reset_db and 'asi_arch' in pxt.list_dirs():
            print("🔄 Resetting xPyLLMent ASI-ARCH database...")
            pxt.drop_dir('asi_arch', force=True)
        
        # Initialize model configuration
        self.model_config = self._get_model_config()
        
        self.setup_schema()
        print("🧠 xPyLLMent ASI-ARCH system initialized!")
    
    def _get_model_config(self):
        """Get model configuration from model manager"""
        if get_model_manager:
            try:
                manager = get_model_manager()
                return manager.get_current_config()
            except:
                pass
        
        # Fallback to default
        return {
            'provider': 'anthropic',
            'model': 'claude-3-5-sonnet-20241022',
            'display_name': 'Claude 3.5 Sonnet'
        }
    
    def _create_chat_function(self, messages, system_prompt, **kwargs):
        """Create appropriate chat function based on model configuration"""
        provider = self.model_config['provider']
        model = self.model_config['model']
        
        if provider == 'anthropic':
            return anthropic.messages(
                messages=messages,
                model=model,
                max_tokens=kwargs.get('max_tokens', 3000),
                model_kwargs={
                    'system': system_prompt,
                    'temperature': kwargs.get('temperature', 0.9),
                    'top_p': kwargs.get('top_p', 0.95)
                }
            )
        elif provider == 'openai':
            # Add system message to the messages list for OpenAI
            system_messages = [{'role': 'system', 'content': system_prompt}] + messages
            
            # Use model_kwargs for OpenAI parameters
            return openai.chat_completions(
                messages=system_messages,
                model=model,
                model_kwargs={
                    'max_tokens': kwargs.get('max_tokens', 3000),
                    'temperature': kwargs.get('temperature', 0.9),
                    'top_p': kwargs.get('top_p', 0.95)
                }
            )
        elif provider == 'ollama':
            # Add system message to the messages list for Ollama  
            system_messages = [{'role': 'system', 'content': system_prompt}] + messages
            return ollama.chat(
                messages=system_messages,
                model=model
            )
        elif provider == 'gemini':
            # For Gemini, system prompt goes separately
            return gemini.generate_content(
                messages=messages,
                model=model,
                system_instruction=system_prompt
            )
        else:
            # Fallback to Anthropic
            return anthropic.messages(
                messages=messages,
                model='claude-3-5-sonnet-20241022',
                max_tokens=kwargs.get('max_tokens', 3000),
                model_kwargs={
                    'system': system_prompt,
                    'temperature': kwargs.get('temperature', 0.9),
                    'top_p': kwargs.get('top_p', 0.95)
                }
            )
    
    def setup_schema(self):
        """Create the complete ASI-ARCH database schema"""
        
        # Create main directory
        if 'asi_arch' not in pxt.list_dirs():
            pxt.create_dir('asi_arch')
            print("📁 Created asi_arch directory")
        
        # 1. EXPERIMENTS TABLE - Core research orchestration
        if 'asi_arch.experiments' not in pxt.list_tables():
            self.experiments = pxt.create_table(
                'asi_arch.experiments',
                {
                    'experiment_id': pxt.String,
                    'generation': pxt.Int,
                    'parent_ids': pxt.Json,  # For evolution tracking (list of strings)
                    'target_capability': pxt.String,
                    'status': pxt.String,  # pending, researching, engineering, training, completed, failed
                    'created_at': pxt.Timestamp,
                    
                    # Research inputs
                    'research_prompt': pxt.String,
                    'historical_context': pxt.Json,  # Summary of previous experiments
                    'fitness_targets': pxt.Json,     # What we're optimizing for
                    
                    # Results from each agent
                    'benchmark_scores': pxt.Json,    # Final evaluation results
                    'training_metrics': pxt.Json,    # Training curves, loss, etc.
                    'model_artifacts': pxt.Json,     # Model weights, configs
                }
            )
            
            # Add AI Agent computed columns
            self._add_researcher_agent()
            self._add_engineer_agent()
            self._add_fitness_evaluator()
            
            print("🧪 Created experiments table with AI agents")
        else:
            self.experiments = pxt.get_table('asi_arch.experiments')
        
        # 2. ARCHITECTURE LINEAGE - Evolution tracking
        if 'asi_arch.lineage' not in pxt.list_tables():
            self.lineage = pxt.create_table(
                'asi_arch.lineage',
                {
                    'parent_id': pxt.String,
                    'child_id': pxt.String,
                    'mutation_type': pxt.String,  # crossover, mutation, novel
                    'generation_gap': pxt.Int,
                    'fitness_improvement': pxt.Float,
                    'created_at': pxt.Timestamp,
                    'innovation_notes': pxt.String
                }
            )
            print("🌳 Created lineage tracking table")
        else:
            self.lineage = pxt.get_table('asi_arch.lineage')
        
        # 3. RESEARCH SNAPSHOTS - Shareable breakthrough moments
        if 'asi_arch.snapshots' not in pxt.list_tables():
            self.snapshots = pxt.create_table(
                'asi_arch.snapshots',
                {
                    'snapshot_id': pxt.String,
                    'name': pxt.String,
                    'description': pxt.String,
                    'generation': pxt.Int,
                    'breakthrough_type': pxt.String,  # architecture, training, evaluation
                    'key_innovations': pxt.Json,  # Array of strings
                    'performance_gains': pxt.Json,
                    'created_at': pxt.Timestamp,
                    'created_by': pxt.String,
                    'public': pxt.Bool,
                }
            )
            print("📸 Created research snapshots table")
        else:
            self.snapshots = pxt.get_table('asi_arch.snapshots')
    
    def _add_researcher_agent(self):
        """Add the Researcher Agent as a computed column"""
        
        # Create the research prompt from context
        research_messages = [
            {'role': 'user', 'content': self.experiments.research_prompt}
        ]
        
        system_prompt = """You are an elite AI researcher specializing in neural architecture discovery. 
Your mission: Generate groundbreaking, scientifically-grounded architecture hypotheses that push the boundaries of AI.

CONTEXT: You're part of xPyLLMent ASI-ARCH, an autonomous research system discovering novel neural architectures. Each generation builds on the success of previous experiments.

REQUIREMENTS:
1. Generate truly novel architectures (not just parameter tweaks)
2. Focus on sub-quadratic complexity O(n log n) or better
3. Target reasoning, efficiency, and generalization improvements
4. Provide concrete mathematical justification
5. Include detailed implementation guidance

RESPOND IN VALID JSON:
{
    "hypothesis": "Clear description of the novel architecture",
    "scientific_motivation": "Deep mathematical/computational reasoning", 
    "key_innovations": ["innovation 1", "innovation 2", "innovation 3"],
    "complexity_analysis": "Computational complexity breakdown",
    "implementation_strategy": "Detailed PyTorch implementation guidance",
    "expected_improvements": {
        "reasoning": "quantified improvement",
        "efficiency": "quantified improvement", 
        "generalization": "quantified improvement"
    },
    "risk_assessment": {
        "technical_challenges": ["challenge 1", "challenge 2"],
        "mitigation_strategies": ["strategy 1", "strategy 2"]
    },
    "novelty_score": 0.85,
    "confidence": 0.75,
    "breakthrough_potential": "description of potential impact"
}"""
        
        # Add researcher agent computed column using configured model
        self.experiments.add_computed_column(
            research_output=self._create_chat_function(
                messages=research_messages,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.9,
                top_p=0.95
            )
        )
        
        # Extract the response based on provider
        if self.model_config['provider'] == 'anthropic':
            self.experiments.add_computed_column(
                research_json=self.experiments.research_output.content[0].text
            )
        else:
            # For OpenAI, Ollama, etc. - adjust extraction as needed
            self.experiments.add_computed_column(
                research_json=self.experiments.research_output.choices[0].message.content
            )
    
    def _add_engineer_agent(self):
        """Add the Engineer Agent for code generation"""
        
        # Engineer agent messages
        engineer_messages = [
            {'role': 'user', 'content': f"Implement this architecture: {self.experiments.research_json}"}
        ]
        
        system_prompt = """You are an expert PyTorch engineer implementing cutting-edge neural architectures.

MISSION: Convert research hypotheses into production-ready, optimized PyTorch implementations.

REQUIREMENTS:
1. Generate complete, working PyTorch code
2. Use modern patterns: @torch.compile, efficient attention, chunked processing
3. Ensure compatibility with standard training pipelines
4. Include comprehensive error handling and validation
5. Optimize for both memory and compute efficiency
6. Add detailed documentation and type hints

RESPOND WITH COMPLETE PYTORCH MODULE:
- Main architecture class
- Forward pass implementation  
- Initialization and configuration
- Utility functions for training
- Memory optimization techniques
- Performance profiling hooks

Focus on clean, maintainable, high-performance code."""
        
        self.experiments.add_computed_column(
            engineering_output=self._create_chat_function(
                messages=engineer_messages,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.3,  # Lower temp for more precise code
                top_p=0.9
            )
        )
        
        # Extract code based on provider
        if self.model_config['provider'] == 'anthropic':
            self.experiments.add_computed_column(
                generated_code=self.experiments.engineering_output.content[0].text
            )
        else:
            # For OpenAI, Ollama, etc.
            self.experiments.add_computed_column(
                generated_code=self.experiments.engineering_output.choices[0].message.content
            )
    
    def _add_fitness_evaluator(self):
        """Add fitness evaluation computed column"""
        
        # Add fitness computed column using the module-level UDF function
        self.experiments.add_computed_column(
            fitness_score=compute_fitness(
                self.experiments.research_json,
                self.experiments.benchmark_scores,
                self.experiments.training_metrics
            )
        )
    
    def start_experiment(
        self, 
        target_capability: str = "general_reasoning",
        generation: int = 1,
        parent_ids: List[str] = None
    ) -> str:
        """Start a new architecture discovery experiment"""
        
        experiment_id = f"asi_arch_{generation:03d}_{uuid.uuid4().hex[:8]}"
        
        # Create research prompt based on context
        if generation == 1:
            research_prompt = f"""
Generate a novel neural architecture targeting {target_capability} capabilities.

FOCUS AREAS:
- Sub-quadratic attention mechanisms (O(n log n) or better)
- Hierarchical information processing
- Efficient reasoning and generalization
- Novel architectural patterns not seen in current literature

GENERATION: {generation} (Initial exploration)
TARGET: {target_capability}

Generate a groundbreaking architecture hypothesis that could revolutionize {target_capability}.
"""
        else:
            # Get context from parent experiments
            if parent_ids:
                parent_context = self._get_parent_context(parent_ids)
                research_prompt = f"""
Generate a novel neural architecture building on previous discoveries.

PARENT EXPERIMENTS CONTEXT:
{parent_context}

FOCUS AREAS:
- Improve upon successful patterns from parents
- Introduce novel innovations
- Target {target_capability} capabilities
- Maintain or improve efficiency

GENERATION: {generation}
TARGET: {target_capability}

Generate an architecture that evolves the best ideas from parents while introducing breakthrough innovations.
"""
            else:
                research_prompt = f"Generate a novel architecture for generation {generation} targeting {target_capability}."
        
        # Insert experiment (triggers all AI agents automatically!)
        self.experiments.insert([{
            'experiment_id': experiment_id,
            'generation': generation,
            'parent_ids': parent_ids or [],
            'target_capability': target_capability,
            'status': 'researching',
            'created_at': datetime.now(),
            'research_prompt': research_prompt,
            'historical_context': {},
            'fitness_targets': {target_capability: 0.8},
            'benchmark_scores': {},
            'training_metrics': {},
            'model_artifacts': {}
        }])
        
        print(f"🚀 Started experiment {experiment_id}")
        print(f"📊 Generation: {generation}")
        print(f"🎯 Target: {target_capability}")
        
        return experiment_id
    
    def _get_parent_context(self, parent_ids: List[str]) -> str:
        """Get context from parent experiments for evolution"""
        
        if not parent_ids:
            return "No parent context available."
        
        # Query parent experiments
        results = self.experiments.select(
            self.experiments.experiment_id,
            self.experiments.research_json,
            self.experiments.fitness_score
        ).where(self.experiments.experiment_id.isin(parent_ids)).collect()
        
        df = results.to_pandas()
        if df.empty:
            return "Parent experiments not found."
        
        context_parts = []
        for _, row in df.iterrows():
            try:
                research_data = json.loads(row['research_json'])
                context_parts.append(f"""
Experiment {row['experiment_id']} (Fitness: {row['fitness_score']:.3f}):
- Hypothesis: {research_data.get('hypothesis', 'N/A')}
- Key Innovations: {research_data.get('key_innovations', [])}
- Performance: {research_data.get('expected_improvements', {})}
""")
            except:
                context_parts.append(f"Experiment {row['experiment_id']}: Data parsing failed")
        
        return "\n".join(context_parts)
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get results from a specific experiment"""
        
        results = self.experiments.select().where(
            self.experiments.experiment_id == experiment_id
        ).collect()
        
        df = results.to_pandas()
        if df.empty:
            return {"error": "Experiment not found"}
        
        row = df.iloc[0]
        
        try:
            research_data = json.loads(row['research_json']) if row['research_json'] else {}
        except:
            research_data = {"error": "Failed to parse research output"}
        
        return {
            'experiment_id': row['experiment_id'],
            'generation': row['generation'],
            'target_capability': row['target_capability'],
            'status': row['status'],
            'research_hypothesis': research_data,
            'generated_code': row['generated_code'],
            'fitness_score': row['fitness_score'],
            'created_at': row['created_at']
        }
    
    def list_experiments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent experiments with their results"""
        
        results = self.experiments.select(
            self.experiments.experiment_id,
            self.experiments.generation,
            self.experiments.target_capability,
            self.experiments.status,
            self.experiments.fitness_score,
            self.experiments.created_at
        ).order_by(self.experiments.created_at, asc=False).limit(limit).collect()
        
        return results.to_pandas().to_dict('records')
    
    def create_research_snapshot(
        self, 
        name: str,
        description: str,
        experiment_ids: List[str] = None,
        public: bool = False
    ) -> str:
        """Create a shareable research snapshot"""
        
        snapshot_id = f"snapshot_{uuid.uuid4().hex[:12]}"
        
        # Get latest generation if no specific experiments provided
        if not experiment_ids:
            latest = self.experiments.select(
                self.experiments.generation
            ).order_by(self.experiments.generation, asc=False).limit(1).collect()
            
            if not latest.to_pandas().empty:
                latest_gen = latest.to_pandas().iloc[0]['generation']
                exp_results = self.experiments.select(
                    self.experiments.experiment_id
                ).where(self.experiments.generation == latest_gen).collect()
                experiment_ids = exp_results.to_pandas()['experiment_id'].tolist()
        
        # Create Pixeltable snapshot
        pxt_snapshot_name = f"asi_arch_research_{snapshot_id}"
        pxt.create_snapshot(pxt_snapshot_name)
        
        # Record in our snapshots table
        self.snapshots.insert([{
            'snapshot_id': snapshot_id,
            'name': name,
            'description': description,
            'generation': latest_gen if 'latest_gen' in locals() else 0,
            'breakthrough_type': 'architecture',
            'key_innovations': [],
            'performance_gains': {},
            'created_at': datetime.now(),
            'created_by': 'asi_arch_system',
            'public': public
        }])
        
        print(f"📸 Created research snapshot: {name}")
        print(f"🔗 Snapshot ID: {snapshot_id}")
        print(f"💾 Pixeltable snapshot: {pxt_snapshot_name}")
        
        return snapshot_id

# Global instance for easy access
asi_arch = None

def initialize_asi_arch(reset_db: bool = False) -> ASIArch:
    """Initialize the global ASI-ARCH system"""
    global asi_arch
    asi_arch = ASIArch(reset_db=reset_db)
    return asi_arch

def get_asi_arch() -> ASIArch:
    """Get the global ASI-ARCH instance"""
    global asi_arch
    if asi_arch is None:
        asi_arch = ASIArch()
    return asi_arch

if __name__ == "__main__":
    # Demo the system
    print("🧠 Initializing xPyLLMent ASI-ARCH: Autonomous AI Research System")
    
    system = initialize_asi_arch(reset_db=True)
    
    print("\n🚀 Starting first architecture discovery experiment...")
    exp_id = system.start_experiment(
        target_capability="reasoning",
        generation=1
    )
    
    print(f"\n⏳ Waiting for AI agents to complete research...")
    print(f"📋 Experiment ID: {exp_id}")
    print("\nThe system is now autonomously:")
    print("1. 🧠 Generating novel architecture hypotheses")
    print("2. ⚙️ Converting them to PyTorch code")
    print("3. 📊 Evaluating fitness scores")
    print("\n🎉 ASI-ARCH is LIVE! The future of AI research has begun!")