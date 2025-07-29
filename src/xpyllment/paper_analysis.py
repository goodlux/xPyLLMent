"""
Integrated Paper Analysis System for xPyLLMent ASI-ARCH

Combines ArXiv paper ingestion with GLiNER entity extraction 
to create a comprehensive research knowledge base.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from simple_arxiv import SimpleArXivDownloader
from gliner_system import GLiNERSystem, install_gliner

console = Console()

class PaperAnalysisSystem:
    """Integrated system for paper download and entity analysis"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path.home() / '.pixeltable' / 'paper_analysis'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.arxiv_downloader = SimpleArXivDownloader(
            download_dir=self.data_dir / 'arxiv_papers'
        )
        
        # GLiNER system will be initialized when needed
        self.gliner_system = None
        self.gliner_available = False
        
        console.print("📚 Paper Analysis System initialized")
    
    def _ensure_gliner(self) -> bool:
        """Ensure GLiNER is available and initialized"""
        if not self.gliner_available:
            console.print("🛸 Checking GLiNER availability...")
            self.gliner_available = install_gliner()
            
            if self.gliner_available:
                self.gliner_system = GLiNERSystem()
                self.gliner_system.setup_research_tables()
                console.print("✅ GLiNER system ready!")
            else:
                console.print("⚠️  GLiNER not available - entity extraction disabled")
        
        return self.gliner_available
    
    def download_and_analyze_papers(
        self,
        categories: List[str] = None,
        max_papers: int = 10,
        date_range: str = "1w",
        extract_entities: bool = True
    ) -> Dict[str, Any]:
        """Download papers and perform entity analysis"""
        
        console.print(Panel.fit(
            "[bold blue]📥 Paper Download & Analysis Pipeline[/bold blue]\\n"
            "[dim]Downloading papers and extracting research entities[/dim]",
            style="blue"
        ))
        
        # Step 1: Download papers
        console.print("\\n🔍 **Step 1: ArXiv Paper Download**")
        download_results = self.arxiv_downloader.search_and_download(
            categories=categories or ['cs.AI', 'cs.LG', 'cs.CL'],
            max_papers=max_papers,
            date_range=date_range
        )
        
        if download_results['downloaded'] == 0:
            console.print("❌ No papers downloaded - skipping analysis")
            return download_results
        
        # Step 2: Entity extraction (if enabled and available)
        if extract_entities and self._ensure_gliner():
            console.print("\\n🛸 **Step 2: GLiNER Entity Extraction**")
            analysis_results = self._analyze_downloaded_papers()
            
            # Combine results
            return {
                **download_results,
                'entity_analysis': analysis_results,
                'gliner_enabled': True
            }
        else:
            console.print("\\n⏭️  **Skipping entity analysis**")
            return {
                **download_results,
                'entity_analysis': None,
                'gliner_enabled': False
            }
    
    def _analyze_downloaded_papers(self) -> Dict[str, Any]:
        """Analyze recently downloaded papers with GLiNER"""
        
        # Get recently downloaded papers from manifest
        manifest = self.arxiv_downloader.manifest
        recent_papers = [
            p for p in manifest['papers'] 
            if p.get('status') == 'downloaded' and p.get('download_date')
        ]
        
        if not recent_papers:
            return {'analyzed_papers': 0, 'entities_extracted': 0}
        
        analyzed_count = 0
        total_entities = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Extracting entities...", total=len(recent_papers))
            
            for paper_data in recent_papers:
                # Check if already analyzed (basic deduplication)
                if self._paper_already_analyzed(paper_data['arxiv_id']):
                    progress.update(task, advance=1)
                    continue
                
                # Prepare paper for GLiNER analysis
                paper_for_analysis = {
                    'title': paper_data['title'],
                    'abstract': paper_data['abstract'],
                    'full_text': paper_data['abstract'],  # Use abstract as full text for now
                    'authors': paper_data['authors'],
                    'arxiv_id': paper_data['arxiv_id'],
                    'published_date': paper_data['published_date'],
                    'categories': paper_data['categories'],
                    'pdf_path': paper_data.get('pdf_path', ''),
                    'source': 'arxiv'
                }
                
                # Ingest into GLiNER system
                try:
                    paper_id = self.gliner_system.ingest_paper(paper_for_analysis)
                    analyzed_count += 1
                    
                    # Count entities (rough estimate)
                    if paper_data.get('abstract'):
                        # Estimate entity count based on abstract length
                        total_entities += len(paper_data['abstract'].split()) // 10
                    
                except Exception as e:
                    console.print(f"⚠️  Failed to analyze {paper_data['arxiv_id']}: {e}")
                
                progress.update(task, advance=1)
        
        console.print(f"✅ Analyzed {analyzed_count} papers with GLiNER")
        
        return {
            'analyzed_papers': analyzed_count,
            'estimated_entities': total_entities,
            'total_papers_in_db': analyzed_count
        }
    
    def _paper_already_analyzed(self, arxiv_id: str) -> bool:
        """Check if paper is already in GLiNER database"""
        if not self.gliner_system:
            return False
        
        try:
            results = self.gliner_system.papers.select(
                self.gliner_system.papers.paper_id
            ).where(self.gliner_system.papers.arxiv_id == arxiv_id).collect()
            
            return len(results.to_pandas()) > 0
        except:
            return False
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive analysis summary"""
        
        # ArXiv download summary
        arxiv_summary = self.arxiv_downloader.get_summary()
        
        # GLiNER analysis summary
        gliner_summary = {}
        if self.gliner_system:
            try:
                gliner_summary = self.gliner_system.analyze_entity_trends()
            except:
                gliner_summary = {'error': 'GLiNER analysis failed'}
        
        return {
            'arxiv_download': arxiv_summary,
            'entity_analysis': gliner_summary,
            'gliner_available': self.gliner_available
        }
    
    def display_analysis_dashboard(self):
        """Display beautiful analysis dashboard"""
        
        summary = self.get_analysis_summary()
        
        console.print(Panel.fit(
            "[bold cyan]📊 xPyLLMent Research Analysis Dashboard[/bold cyan]\\n"
            "[dim]ArXiv Downloads + GLiNER Entity Extraction[/dim]",
            style="cyan"
        ))
        
        # ArXiv Statistics
        arxiv_data = summary['arxiv_download']
        table = Table(title="📥 ArXiv Download Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(arxiv_data.get('total_papers', 0)))
        table.add_row("Successful Downloads", str(arxiv_data.get('successful_downloads', 0)))
        table.add_row("Recent Papers (30d)", str(arxiv_data.get('recent_papers', 0)))
        table.add_row("Total Size", f"{arxiv_data.get('total_size_mb', 0):.1f} MB")
        
        console.print(table)
        
        # Top Categories
        if arxiv_data.get('top_categories'):
            console.print("\\n🏷️  **Top Categories**")
            for category, count in list(arxiv_data['top_categories'].items())[:5]:
                console.print(f"  {category}: {count} papers")
        
        # GLiNER Analysis
        if self.gliner_available and summary['entity_analysis']:
            entity_data = summary['entity_analysis']
            
            if 'error' not in entity_data:
                console.print("\\n🛸 **GLiNER Entity Analysis**")
                console.print(f"📊 Papers Analyzed: {entity_data.get('total_papers_analyzed', 0)}")
                console.print(f"🏷️  Unique Entities: {entity_data.get('total_unique_entities', 0)}")
                console.print(f"📝 Entity Types: {entity_data.get('total_unique_types', 0)}")
                
                # Top entities preview
                if entity_data.get('top_entities'):
                    console.print("\\n🔥 **Most Frequent Research Terms**")
                    for entity, freq in entity_data['top_entities'][:8]:
                        console.print(f"  {entity}: {freq} mentions")
        else:
            console.print("\\n🛸 **GLiNER Status**: Not available or configured")
    
    def analyze_specific_paper(self, arxiv_id: str):
        """Analyze a specific paper by ArXiv ID"""
        
        if not self._ensure_gliner():
            console.print("❌ GLiNER not available")
            return
        
        # Find paper in GLiNER database
        try:
            results = self.gliner_system.papers.select(
                self.gliner_system.papers.paper_id,
                self.gliner_system.papers.title
            ).where(self.gliner_system.papers.arxiv_id == arxiv_id).collect()
            
            df = results.to_pandas()
            if df.empty:
                console.print(f"❌ Paper {arxiv_id} not found in analysis database")
                return
            
            paper_id = df.iloc[0]['paper_id']
            self.gliner_system.display_entity_analysis(paper_id)
            
        except Exception as e:
            console.print(f"❌ Error analyzing paper: {e}")

def demo_paper_analysis():
    """Demo the integrated paper analysis system"""
    
    console.print("🧬 [bold cyan]xPyLLMent Paper Analysis Demo[/bold cyan]")
    
    # Initialize system
    system = PaperAnalysisSystem()
    
    # Download and analyze a few papers
    console.print("\\n📥 Downloading recent AI papers...")
    results = system.download_and_analyze_papers(
        categories=['cs.AI', 'cs.LG'],
        max_papers=3,
        date_range='1w',
        extract_entities=True
    )
    
    console.print(f"\\n✅ Downloaded: {results['downloaded']} papers")
    console.print(f"❌ Failed: {results['failed']} papers")
    
    if results.get('entity_analysis'):
        analysis = results['entity_analysis']
        console.print(f"🛸 Analyzed: {analysis['analyzed_papers']} papers")
        console.print(f"🏷️  Entities: ~{analysis['estimated_entities']} extracted")
    
    # Show dashboard
    console.print("\\n" + "="*60)
    system.display_analysis_dashboard()

if __name__ == "__main__":
    demo_paper_analysis()