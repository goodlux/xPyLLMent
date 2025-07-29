"""
Pixeltable-Native GLiNER Analysis System for xPyLLMent ASI-ARCH

Uses the official Pixeltable GLiNER functions we just added to the HuggingFace module.
This is the PROPER way to do entity extraction in Pixeltable! 💪
"""

import pixeltable as pxt
from pixeltable.functions.huggingface import gliner_entity_extraction, gliner_research_entities, gliner_quick_entities
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

class PixeltableGLiNERSystem:
    """GLiNER Entity Extraction using Official Pixeltable Functions"""
    
    def __init__(self, reset_db: bool = False):
        self.console = Console()
        pxt.init()
        
        if reset_db and 'research_entities' in pxt.list_dirs():
            console.print("🔄 Resetting research entities database...")
            pxt.drop_dir('research_entities', force=True)
        
        self.setup_schema()
        console.print("🛸 Pixeltable GLiNER system initialized!")
    
    def setup_schema(self):
        """Set up research papers table with official Pixeltable GLiNER functions"""
        
        # Create directory
        if 'research_entities' not in pxt.list_dirs():
            pxt.create_dir('research_entities')
            console.print("📁 Created research_entities directory")
        
        # Papers table with entity extraction
        if 'research_entities.papers' not in pxt.list_tables():
            self.papers = pxt.create_table(
                'research_entities.papers',
                {
                    'paper_id': pxt.String,
                    'title': pxt.String,
                    'abstract': pxt.String,
                    'full_text': pxt.String,
                    'authors': pxt.Json,
                    'arxiv_id': pxt.String,
                    'published_date': pxt.String,
                    'categories': pxt.Json,
                    'pdf_path': pxt.String,
                    'source': pxt.String,
                    'ingestion_date': pxt.Timestamp
                }
            )
            
            console.print("🛸 Adding official Pixeltable GLiNER computed columns...")
            
            # 1. Research entities from abstract (specialized function)
            self.papers.add_computed_column(
                abstract_research_entities=gliner_research_entities(
                    self.papers.abstract,
                    threshold=0.6
                )
            )
            
            # 2. Quick entities from title (fast extraction)
            self.papers.add_computed_column(
                title_quick_entities=gliner_quick_entities(
                    self.papers.title,
                    threshold=0.7
                )
            )
            
            # 3. Custom entity extraction for full text with specific research terms
            self.papers.add_computed_column(
                full_text_entities=gliner_entity_extraction(
                    self.papers.full_text,
                    entity_types=[
                        "neural network", "transformer", "attention", "embedding",
                        "algorithm", "method", "technique", "approach", "framework",
                        "dataset", "benchmark", "metric", "evaluation", "experiment",
                        "accuracy", "precision", "recall", "loss", "performance",
                        "paper", "model", "architecture", "training", "optimization"
                    ],
                    threshold=0.5
                )
            )
            
            # 4. PII detection for author information (using specialized model)
            self.papers.add_computed_column(
                author_pii_entities=gliner_entity_extraction(
                    self.papers.abstract,  # Check abstract for PII
                    model_id="urchade/gliner_multi_pii-v1",
                    entity_types=["person", "email", "phone", "organization", "location"],
                    threshold=0.8
                )
            )
            
            console.print("✅ Papers table with official Pixeltable GLiNER functions created!")
        else:
            self.papers = pxt.get_table('research_entities.papers')
    
    def ingest_paper(self, paper_data: Dict[str, Any]) -> str:
        """Ingest a paper - entity extraction happens automatically via computed columns!"""
        
        import uuid
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        
        # Insert paper - ALL GLiNER extractions happen automatically!
        self.papers.insert([{
            'paper_id': paper_id,
            'title': paper_data.get('title', ''),
            'abstract': paper_data.get('abstract', ''),
            'full_text': paper_data.get('full_text', paper_data.get('abstract', '')),
            'authors': paper_data.get('authors', []),
            'arxiv_id': paper_data.get('arxiv_id', ''),
            'published_date': paper_data.get('published_date', ''),
            'categories': paper_data.get('categories', []),
            'pdf_path': paper_data.get('pdf_path', ''),
            'source': paper_data.get('source', 'unknown'),
            'ingestion_date': datetime.now()
        }])
        
        console.print(f"🛸 Paper ingested with Pixeltable GLiNER analysis: {paper_id}")
        return paper_id
    
    def get_paper_entities(self, paper_id: str) -> Dict[str, Any]:
        """Get ALL entity extractions for a paper"""
        
        results = self.papers.select(
            self.papers.paper_id,
            self.papers.title,
            self.papers.abstract_research_entities,
            self.papers.title_quick_entities,
            self.papers.full_text_entities,
            self.papers.author_pii_entities
        ).where(self.papers.paper_id == paper_id).collect()
        
        df = results.to_pandas()
        if df.empty:
            return {'error': 'Paper not found'}
        
        row = df.iloc[0]
        return {
            'paper_id': row['paper_id'],
            'title': row['title'],
            'abstract_research_entities': row['abstract_research_entities'],
            'title_quick_entities': row['title_quick_entities'], 
            'full_text_entities': row['full_text_entities'],
            'author_pii_entities': row['author_pii_entities']
        }
    
    def analyze_entity_trends(self, limit: int = 20) -> Dict[str, Any]:
        """Analyze entity trends across all papers using official Pixeltable functions"""
        
        # Get all papers with entities
        results = self.papers.select(
            self.papers.abstract_research_entities,
            self.papers.full_text_entities,
            self.papers.title_quick_entities
        ).collect()
        
        df = results.to_pandas()
        
        entity_freq = {}
        entity_types_freq = {}
        
        # Process different entity extraction results
        for _, row in df.iterrows():
            # Process abstract research entities
            if row['abstract_research_entities'] and 'entities' in row['abstract_research_entities']:
                for entity in row['abstract_research_entities']['entities']:
                    text = entity['text'].lower()
                    entity_type = entity['label']
                    
                    entity_freq[text] = entity_freq.get(text, 0) + 1
                    entity_types_freq[entity_type] = entity_types_freq.get(entity_type, 0) + 1
            
            # Process full text entities
            if row['full_text_entities'] and 'entities' in row['full_text_entities']:
                for entity in row['full_text_entities']['entities']:
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
                f"[bold cyan]🛸 Official Pixeltable GLiNER Analysis[/bold cyan]\\n"
                f"[dim]Paper: {entities['title'][:60]}...[/dim]",
                style="cyan"
            ))
            
            # Abstract research entities (using specialized function)
            if entities.get('abstract_research_entities') and entities['abstract_research_entities'].get('entities'):
                table = Table(title="📄 Abstract Research Entities (gliner_research_entities)", show_header=True)
                table.add_column("Entity", style="cyan")
                table.add_column("Type", style="green") 
                table.add_column("Confidence", style="yellow")
                
                for entity in entities['abstract_research_entities']['entities'][:15]:
                    table.add_row(
                        entity['text'][:30],
                        entity['label'],
                        f"{entity['confidence']:.3f}"
                    )
                console.print(table)
            
            # Title quick entities
            if entities.get('title_quick_entities') and entities['title_quick_entities'].get('entities'):
                console.print(f"\\n🚀 **Title Entities (gliner_quick_entities)**: ", end="")
                title_entities = [e['text'] for e in entities['title_quick_entities']['entities'][:5]]
                console.print(", ".join(title_entities))
            
            # Full text custom entities
            if entities.get('full_text_entities'):
                ft_data = entities['full_text_entities']
                console.print(f"\\n📖 **Full Text Entities (custom)**: {ft_data.get('total_entities', 0)} found")
                console.print(f"🏷️  Types: {', '.join(ft_data.get('entity_types_found', [])[:6])}")
            
            # PII detection results
            if entities.get('author_pii_entities') and entities['author_pii_entities'].get('entities'):
                console.print(f"\\n🔒 **PII Detected**: {len(entities['author_pii_entities']['entities'])} items")
                
        else:
            # Show overall trends
            trends = self.analyze_entity_trends()
            
            console.print(Panel.fit(
                f"[bold cyan]🛸 Pixeltable GLiNER Research Trends[/bold cyan]\\n"
                f"[dim]Entity patterns across {trends['total_papers_analyzed']} papers[/dim]",
                style="cyan"
            ))
            
            # Top entities table
            table = Table(title="🔥 Most Frequent Research Entities", show_header=True)
            table.add_column("Entity", style="cyan")
            table.add_column("Frequency", style="green")
            table.add_column("Source", style="dim")
            
            for entity_text, freq in trends['top_entities'][:15]:
                table.add_row(entity_text, str(freq), "Pixeltable GLiNER")
            
            console.print(table)
            
            # Entity types distribution  
            console.print(f"\\n📊 **Entity Type Distribution**")
            for entity_type, count in trends['top_entity_types'][:10]:
                console.print(f"  {entity_type}: {count}")
    
    def get_paper_count(self) -> int:
        """Get total number of papers in the system"""
        try:
            results = self.papers.select(self.papers.paper_id).collect()
            return len(results.to_pandas())
        except:
            return 0

def demo_pixeltable_gliner():
    """Demo the official Pixeltable GLiNER integration"""
    
    console.print("🛸 [bold cyan]Official Pixeltable GLiNER Demo[/bold cyan]")
    console.print("Using the GLiNER functions we just added to Pixeltable! 💪")
    
    # Initialize system
    system = PixeltableGLiNERSystem(reset_db=True)
    
    # Demo papers with different content types
    demo_papers = [
        {
            'title': 'Attention Is All You Need: Transformer Networks for Neural Machine Translation',
            'abstract': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on machine translation tasks show these models achieve superior quality while being more parallelizable.',
            'full_text': 'The Transformer architecture uses multi-head self-attention and position-wise fully connected feed-forward networks. We trained models on WMT 2014 English-to-German and English-to-French translation tasks achieving new state-of-the-art BLEU scores.',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
            'source': 'demo',
            'categories': ['cs.CL', 'cs.LG']
        },
        {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
            'abstract': 'We introduce BERT, designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context. BERT advances the state-of-the-art for eleven natural language processing tasks.',
            'full_text': 'BERT is trained using masked language modeling and next sentence prediction. The model achieves significant improvements on GLUE benchmark, SQuAD v1.1, and SQuAD v2.0 datasets with F1 scores of 93.2 and 83.1 respectively.',
            'authors': ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee'],
            'source': 'demo',
            'categories': ['cs.CL', 'cs.AI']
        }
    ]
    
    # Ingest papers
    console.print("\\n📥 Ingesting demo papers...")
    paper_ids = []
    for paper in demo_papers:
        paper_id = system.ingest_paper(paper)
        paper_ids.append(paper_id)
    
    console.print("⏳ Processing with official Pixeltable GLiNER functions...")
    import time
    time.sleep(3)  # Give time for processing
    
    # Display results
    console.print("\\n" + "="*70)
    for paper_id in paper_ids:
        system.display_entity_analysis(paper_id)
        console.print("\\n" + "-"*50 + "\\n")
    
    # Show overall trends
    console.print("\\n" + "="*70)
    system.display_entity_analysis()

if __name__ == "__main__":
    demo_pixeltable_gliner()