"""
GLiNER Entity Extraction System for xPyLLMent ASI-ARCH

Integrates GLiNER (the entity-extracting GLEEK 👽) with Pixeltable
for autonomous research paper analysis and entity extraction.
"""

import pixeltable as pxt
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import tempfile
import re

console = Console()

# GLiNER entity extraction UDF
@pxt.udf
def extract_entities_gliner(
    text: str, 
    entity_types: List[str],
    model_name: str = "urchade/gliner_base",
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Extract entities from text using GLiNER
    
    Args:
        text: Input text to analyze
        entity_types: List of entity types to extract (e.g., ["person", "organization", "location"])
        model_name: GLiNER model to use
        threshold: Confidence threshold for entity extraction
        
    Returns:
        Dictionary with extracted entities and metadata
    """
    try:
        # Import GLiNER (lazy import to avoid startup overhead)
        from gliner import GLiNER
        
        # Cache model to avoid reloading
        if not hasattr(extract_entities_gliner, '_model_cache'):
            extract_entities_gliner._model_cache = {}
            
        if model_name not in extract_entities_gliner._model_cache:
            console.print(f"🛸 Loading GLiNER model: {model_name}")
            extract_entities_gliner._model_cache[model_name] = GLiNER.from_pretrained(model_name)
        
        model = extract_entities_gliner._model_cache[model_name]
        
        # Extract entities
        entities = model.predict_entities(text, entity_types, threshold=threshold)
        
        # Process results
        extracted = []
        entity_counts = {}
        
        for entity in entities:
            entity_info = {
                'text': entity['text'],
                'label': entity['label'],
                'start': entity['start'],
                'end': entity['end'],
                'confidence': entity.get('score', 0.0)
            }
            extracted.append(entity_info)
            
            # Count entity types
            label = entity['label']
            entity_counts[label] = entity_counts.get(label, 0) + 1
        
        return {
            'entities': extracted,
            'entity_counts': entity_counts,
            'total_entities': len(extracted),
            'entity_types_found': list(entity_counts.keys()),
            'model_used': model_name,
            'threshold': threshold
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'entities': [],
            'entity_counts': {},
            'total_entities': 0,
            'entity_types_found': [],
            'model_used': model_name,
            'threshold': threshold
        }

# Research-specific entity extraction UDF
@pxt.udf
def extract_research_entities(text: str, threshold: float = 0.4) -> Dict[str, Any]:
    """
    Extract research-specific entities from academic papers
    
    Optimized for AI/ML research papers with domain-specific entity types
    """
    research_entity_types = [
        # Technical entities
        "algorithm", "model", "architecture", "method", "technique", "approach",
        
        # Research artifacts
        "dataset", "benchmark", "metric", "evaluation", "experiment", 
        "baseline", "framework", "library", "tool",
        
        # Academic entities  
        "paper", "publication", "journal", "conference", "workshop",
        "author", "researcher", "institution", "university",
        
        # AI/ML specific
        "neural network", "transformer", "attention", "embedding", 
        "loss function", "optimizer", "hyperparameter", "activation",
        
        # Performance measures
        "accuracy", "precision", "recall", "f1-score", "perplexity",
        "bleu score", "rouge score", "loss", "error rate",
        
        # General entities
        "person", "organization", "location", "date", "number", "percentage"
    ]
    
    return extract_entities_gliner(text, research_entity_types, threshold=threshold)

# Lightweight entity extraction for paper abstracts
@pxt.udf  
def extract_abstract_entities(abstract: str, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Extract key entities from paper abstracts
    
    Focused on the most important entity types for research paper classification
    """
    abstract_entity_types = [
        "method", "model", "algorithm", "dataset", "metric", 
        "performance", "improvement", "technique", "approach"
    ]
    
    return extract_entities_gliner(abstract, abstract_entity_types, threshold=threshold)

class GLiNERSystem:
    """GLiNER Entity Extraction System for Research Analysis"""
    
    def __init__(self):
        self.console = Console()
        self.available_models = {
            'base': 'urchade/gliner_base',
            'small': 'urchade/gliner_small-v2.1',
            'medium': 'urchade/gliner_medium-v2.1', 
            'large': 'urchade/gliner_large-v2.1',
            'multi': 'urchade/gliner_multi-v2.1',
            'pii': 'urchade/gliner_multi_pii-v1'
        }
        
        self.research_entity_types = [
            # Core ML/AI entities
            "neural network", "transformer", "attention mechanism", "embedding",
            "convolution", "lstm", "gru", "rnn", "cnn", "autoencoder", "gan",
            
            # Algorithms & Methods  
            "algorithm", "method", "technique", "approach", "framework",
            "optimization", "gradient descent", "backpropagation", "fine-tuning",
            
            # Research artifacts
            "dataset", "benchmark", "baseline", "metric", "evaluation",
            "experiment", "model", "architecture", "loss function", "optimizer",
            
            # Performance & Results
            "accuracy", "precision", "recall", "f1-score", "auc", "loss",
            "perplexity", "bleu", "rouge", "meteor", "bert-score",
            
            # Academic context
            "paper", "publication", "conference", "journal", "workshop",
            "author", "researcher", "institution", "university",
            
            # General entities
            "person", "organization", "location", "date", "number", "percentage"
        ]
    
    def setup_research_tables(self, force_reset: bool = False):
        """Set up tables for research entity extraction"""
        
        pxt.init()
        
        # Create research analysis directory
        if 'research_analysis' not in pxt.list_dirs():
            pxt.create_dir('research_analysis')
            console.print("📁 Created research_analysis directory")
        elif force_reset:
            pxt.drop_dir('research_analysis', force=True)
            pxt.create_dir('research_analysis')
            console.print("🔄 Reset research_analysis directory")
        
        # Papers table with entity extraction
        if 'research_analysis.papers' not in pxt.list_tables():
            self.papers = pxt.create_table(
                'research_analysis.papers',
                {
                    'paper_id': pxt.String,
                    'title': pxt.String,
                    'abstract': pxt.String,
                    'full_text': pxt.String,
                    'authors': pxt.Json,  # List of author names
                    'arxiv_id': pxt.String,
                    'published_date': pxt.String,
                    'categories': pxt.Json,  # ArXiv categories
                    'pdf_path': pxt.String,
                    'source': pxt.String,  # arxiv, local, etc.
                    'ingestion_date': pxt.Timestamp
                }
            )
            
            # Add entity extraction computed columns
            console.print("🛸 Adding GLiNER entity extraction columns...")
            
            # Abstract entity extraction (lightweight)
            self.papers.add_computed_column(
                abstract_entities=extract_abstract_entities(
                    self.papers.abstract,
                    threshold=0.5
                )
            )
            
            # Full research entity extraction  
            self.papers.add_computed_column(
                research_entities=extract_research_entities(
                    self.papers.full_text,
                    threshold=0.4
                )
            )
            
            # Title entity extraction
            self.papers.add_computed_column(
                title_entities=extract_entities_gliner(
                    self.papers.title,
                    ["method", "model", "algorithm", "technique", "dataset"],
                    threshold=0.6
                )
            )
            
            console.print("✅ Papers table with GLiNER extraction created!")
        else:
            self.papers = pxt.get_table('research_analysis.papers')
        
        # Entity summary table
        if 'research_analysis.entity_summary' not in pxt.list_tables():
            self.entity_summary = pxt.create_table(
                'research_analysis.entity_summary',
                {
                    'entity_text': pxt.String,
                    'entity_type': pxt.String,
                    'frequency': pxt.Int,
                    'papers': pxt.Json,  # List of paper_ids where this entity appears
                    'avg_confidence': pxt.Float,
                    'first_seen': pxt.Timestamp,
                    'last_seen': pxt.Timestamp
                }
            )
            console.print("📊 Entity summary table created!")
        else:
            self.entity_summary = pxt.get_table('research_analysis.entity_summary')
    
    def ingest_paper(self, paper_data: Dict[str, Any]) -> str:
        """Ingest a paper for entity extraction analysis"""
        
        import uuid
        from datetime import datetime
        
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        
        # Insert paper - this will trigger all entity extraction automatically!
        self.papers.insert([{
            'paper_id': paper_id,
            'title': paper_data.get('title', ''),
            'abstract': paper_data.get('abstract', ''),
            'full_text': paper_data.get('full_text', paper_data.get('abstract', '')),  # Use abstract if no full text
            'authors': paper_data.get('authors', []),
            'arxiv_id': paper_data.get('arxiv_id', ''),
            'published_date': paper_data.get('published_date', ''),
            'categories': paper_data.get('categories', []),
            'pdf_path': paper_data.get('pdf_path', ''),
            'source': paper_data.get('source', 'unknown'),
            'ingestion_date': datetime.now()
        }])
        
        console.print(f"🛸 Paper ingested with GLiNER analysis: {paper_id}")
        return paper_id
    
    def get_paper_entities(self, paper_id: str) -> Dict[str, Any]:
        """Get extracted entities for a specific paper"""
        
        results = self.papers.select(
            self.papers.paper_id,
            self.papers.title,
            self.papers.abstract_entities,
            self.papers.research_entities,
            self.papers.title_entities
        ).where(self.papers.paper_id == paper_id).collect()
        
        df = results.to_pandas()
        if df.empty:
            return {'error': 'Paper not found'}
        
        row = df.iloc[0]
        return {
            'paper_id': row['paper_id'],
            'title': row['title'],
            'abstract_entities': row['abstract_entities'],
            'research_entities': row['research_entities'],
            'title_entities': row['title_entities']
        }
    
    def analyze_entity_trends(self, limit: int = 20) -> Dict[str, Any]:
        """Analyze entity trends across all papers"""
        
        # Get all papers with entities
        results = self.papers.select(
            self.papers.research_entities,
            self.papers.abstract_entities,
            self.papers.title_entities
        ).collect()
        
        df = results.to_pandas()
        
        # Aggregate entity counts
        entity_freq = {}
        entity_types_freq = {}
        
        for _, row in df.iterrows():
            # Process research entities
            if row['research_entities'] and 'entities' in row['research_entities']:
                for entity in row['research_entities']['entities']:
                    text = entity['text'].lower()
                    entity_type = entity['label']
                    
                    entity_freq[text] = entity_freq.get(text, 0) + 1
                    entity_types_freq[entity_type] = entity_types_freq.get(entity_type, 0) + 1
        
        # Sort by frequency
        top_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)[:limit]
        top_types = sorted(entity_types_freq.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            'total_papers_analyzed': len(df),
            'top_entities': top_entities,
            'top_entity_types': top_types,
            'total_unique_entities': len(entity_freq),
            'total_unique_types': len(entity_types_freq)
        }
    
    def display_entity_analysis(self, paper_id: str = None):
        """Display beautiful entity analysis results"""
        
        if paper_id:
            # Show analysis for specific paper
            entities = self.get_paper_entities(paper_id)
            
            if 'error' in entities:
                console.print(f"❌ {entities['error']}")
                return
            
            console.print(Panel.fit(
                f"[bold cyan]🛸 GLiNER Entity Analysis[/bold cyan]\\n"
                f"[dim]Paper: {entities['title'][:60]}...[/dim]",
                style="cyan"
            ))
            
            # Abstract entities
            if entities.get('abstract_entities') and entities['abstract_entities'].get('entities'):
                table = Table(title="📄 Abstract Entities", show_header=True)
                table.add_column("Entity", style="cyan")
                table.add_column("Type", style="green") 
                table.add_column("Confidence", style="yellow")
                
                for entity in entities['abstract_entities']['entities'][:10]:
                    table.add_row(
                        entity['text'],
                        entity['label'],
                        f"{entity['confidence']:.2f}"
                    )
                console.print(table)
            
            # Research entities summary
            if entities.get('research_entities'):
                re_data = entities['research_entities']
                console.print(f"\\n🔬 Research Entities: {re_data.get('total_entities', 0)} found")
                console.print(f"🏷️  Types: {', '.join(re_data.get('entity_types_found', [])[:5])}")
                
        else:
            # Show overall trends
            trends = self.analyze_entity_trends()
            
            console.print(Panel.fit(
                f"[bold cyan]🛸 GLiNER Research Trends[/bold cyan]\\n"
                f"[dim]Entity patterns across {trends['total_papers_analyzed']} papers[/dim]",
                style="cyan"
            ))
            
            # Top entities table
            table = Table(title="🔥 Most Frequent Research Entities", show_header=True)
            table.add_column("Entity", style="cyan")
            table.add_column("Frequency", style="green")
            table.add_column("Type", style="dim")
            
            for entity_text, freq in trends['top_entities'][:15]:
                table.add_row(entity_text, str(freq), "research_term")
            
            console.print(table)
            
            # Entity types distribution  
            console.print(f"\\n📊 **Entity Distribution**")
            for entity_type, count in trends['top_entity_types'][:8]:
                console.print(f"  {entity_type}: {count}")

def install_gliner():
    """Install GLiNER if not available"""
    try:
        import gliner
        console.print("✅ GLiNER already installed")
        return True
    except ImportError:
        console.print("🛸 Installing GLiNER...")
        import subprocess
        import sys
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gliner"])
            console.print("✅ GLiNER installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install GLiNER: {e}")
            return False

def demo_gliner_system():
    """Demo the GLiNER system"""
    console.print("🛸 [bold cyan]GLiNER Entity Extraction Demo[/bold cyan]")
    
    # Install GLiNER if needed
    if not install_gliner():
        return
    
    # Setup system
    system = GLiNERSystem()
    system.setup_research_tables(force_reset=True)
    
    # Demo paper
    demo_paper = {
        'title': 'Attention Is All You Need: Transformer Networks for Natural Language Processing',
        'abstract': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.',
        'full_text': 'This paper introduces the Transformer architecture using multi-head self-attention. The model achieves state-of-the-art results on WMT 2014 English-to-German translation and WMT 2014 English-to-French translation tasks. The architecture relies entirely on attention mechanisms and feed-forward networks.',
        'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
        'source': 'demo',
        'categories': ['cs.CL', 'cs.LG']
    }
    
    # Ingest paper with entity extraction
    paper_id = system.ingest_paper(demo_paper)
    
    console.print("⏳ Processing entities...")
    import time
    time.sleep(2)  # Give time for processing
    
    # Display results
    system.display_entity_analysis(paper_id)

if __name__ == "__main__":
    demo_gliner_system()