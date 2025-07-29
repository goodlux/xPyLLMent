"""
ArXiv Paper Ingestion System for ASI-ARCH

Downloads, processes, and ingests research papers from ArXiv into Pixeltable
for use by AI research agents.
"""

import arxiv
import pixeltable as pxt
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
import hashlib
import json
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

class ArXivIngestionSystem:
    """
    Manages download and ingestion of ArXiv papers into Pixeltable
    """
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path.home() / '.pixeltable' / 'arxiv_papers'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize or get the papers table
        self.papers_table = self._get_or_create_papers_table()
        
    def _get_or_create_papers_table(self):
        """Get or create the papers table in Pixeltable"""
        
        try:
            # Try to get existing table
            return pxt.get_table('asi_arch.papers')
        except:
            # Create new table
            try:
                pxt.create_dir('asi_arch')
            except:
                pass  # Directory might already exist
            
            # Create papers table with rich schema
            papers_table = pxt.create_table(
                'asi_arch.papers',
                {
                    'arxiv_id': pxt.String,
                    'title': pxt.String, 
                    'abstract': pxt.String,
                    'authors': pxt.Json,  # List of author names
                    'categories': pxt.Json,  # List of categories
                    'published_date': pxt.Timestamp,
                    'updated_date': pxt.Timestamp,
                    'pdf_url': pxt.String,
                    'pdf_path': pxt.String,  # Local file path
                    'paper_text': pxt.String,  # Extracted text content
                    'embedding': pxt.Json,  # Future: text embeddings as JSON array
                    'download_date': pxt.Timestamp,
                    'file_size': pxt.Int,
                    'processing_status': pxt.String,  # 'downloaded', 'processed', 'failed'
                    'relevance_score': pxt.Float,  # How relevant to AI/ML research
                    'metadata': pxt.Json  # Additional metadata
                }
            )
            
            console.print("✅ Created new papers table in Pixeltable")
            return papers_table
    
    def search_papers(
        self, 
        categories: List[str] = None,
        keywords: List[str] = None,
        max_results: int = 100,
        date_range: str = "1m"
    ) -> List[Dict]:
        """
        Search ArXiv for papers matching criteria
        
        Args:
            categories: ArXiv categories like ['cs.AI', 'cs.LG']
            keywords: Keywords to search for in titles/abstracts
            max_results: Maximum number of papers to return
            date_range: Date range like '1d', '1w', '1m', '3m', '6m'
            
        Returns:
            List of paper metadata dictionaries
        """
        
        # Default categories for AI/ML research
        if not categories:
            categories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE']
        
        # Build search query
        category_query = ' OR '.join([f'cat:{cat}' for cat in categories])
        
        if keywords:
            keyword_query = ' OR '.join([f'ti:{kw} OR abs:{kw}' for kw in keywords])
            query = f'({category_query}) AND ({keyword_query})'
        else:
            query = category_query
        
        # Calculate date filter
        date_filter = self._get_date_filter(date_range)
        
        console.print(f"🔍 Searching ArXiv with query: {query}")
        console.print(f"📅 Date range: {date_range} ({date_filter})")
        
        # Search ArXiv
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Fetching papers from ArXiv...", total=max_results)
            
            for i, result in enumerate(search.results()):
                if i >= max_results:
                    break
                
                # Filter by date if specified
                if date_filter and result.published < date_filter:
                    continue
                
                paper_data = {
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'abstract': result.summary,
                    'authors': [author.name for author in result.authors],
                    'categories': result.categories,
                    'published_date': result.published,
                    'updated_date': result.updated,
                    'pdf_url': result.pdf_url,
                    'relevance_score': self._calculate_relevance(result)
                }
                
                papers.append(paper_data)
                progress.update(task, advance=1)
        
        console.print(f"✅ Found {len(papers)} papers matching criteria")
        return papers
    
    def download_papers(self, papers: List[Dict], max_concurrent: int = 3) -> List[Dict]:
        """
        Download PDF files for papers
        
        Args:
            papers: List of paper metadata
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            Updated papers list with download info
        """
        
        downloaded_papers = []
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            download_task = progress.add_task("Downloading papers...", total=len(papers))
            
            for paper in papers:
                try:
                    # Create safe filename
                    safe_title = "".join(c for c in paper['title'][:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{paper['arxiv_id'].replace('/', '_')}_{safe_title}.pdf"
                    file_path = self.data_dir / filename
                    
                    # Skip if already downloaded
                    if file_path.exists():
                        paper.update({
                            'pdf_path': str(file_path),
                            'file_size': file_path.stat().st_size,
                            'download_date': datetime.now(),
                            'processing_status': 'downloaded'
                        })
                        downloaded_papers.append(paper)
                        progress.update(download_task, advance=1)
                        continue
                    
                    # Download PDF
                    response = requests.get(paper['pdf_url'], stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Update paper info
                    paper.update({
                        'pdf_path': str(file_path),
                        'file_size': file_path.stat().st_size,
                        'download_date': datetime.now(),
                        'processing_status': 'downloaded'
                    })
                    
                    downloaded_papers.append(paper)
                    
                except Exception as e:
                    console.print(f"❌ Failed to download {paper['arxiv_id']}: {e}")
                    paper.update({
                        'processing_status': 'failed',
                        'metadata': {'error': str(e)}
                    })
                    downloaded_papers.append(paper)
                
                progress.update(download_task, advance=1)
        
        successful_downloads = len([p for p in downloaded_papers if p.get('processing_status') == 'downloaded'])
        console.print(f"✅ Successfully downloaded {successful_downloads}/{len(papers)} papers")
        
        return downloaded_papers
    
    def ingest_papers_to_pixeltable(self, papers: List[Dict]) -> int:
        """
        Ingest papers into Pixeltable database
        
        Args:
            papers: List of paper data with download info
            
        Returns:
            Number of papers successfully ingested
        """
        
        ingested_count = 0
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(), 
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            ingest_task = progress.add_task("Ingesting papers to Pixeltable...", total=len(papers))
            
            for paper in papers:
                try:
                    # Check if paper already exists
                    existing = self.papers_table.select().where(
                        self.papers_table.arxiv_id == paper['arxiv_id']
                    ).limit(1).collect()
                    
                    if not existing.empty:
                        progress.update(ingest_task, advance=1)
                        continue
                    
                    # Prepare data for insertion
                    insert_data = {
                        'arxiv_id': paper['arxiv_id'],
                        'title': paper['title'],
                        'abstract': paper['abstract'],
                        'authors': paper['authors'],
                        'categories': paper['categories'],
                        'published_date': paper['published_date'],
                        'updated_date': paper['updated_date'],
                        'pdf_url': paper['pdf_url'],
                        'pdf_path': paper.get('pdf_path', ''),
                        'paper_text': '',  # Will be populated by text extraction
                        'download_date': paper.get('download_date', datetime.now()),
                        'file_size': paper.get('file_size', 0),
                        'processing_status': paper.get('processing_status', 'pending'),
                        'relevance_score': paper.get('relevance_score', 0.5),
                        'metadata': paper.get('metadata', {})
                    }
                    
                    # Insert into Pixeltable
                    self.papers_table.insert([insert_data])
                    ingested_count += 1
                    
                except Exception as e:
                    console.print(f"❌ Failed to ingest {paper['arxiv_id']}: {e}")
                
                progress.update(ingest_task, advance=1)
        
        console.print(f"✅ Successfully ingested {ingested_count} papers into Pixeltable")
        return ingested_count
    
    def run_full_ingestion(
        self,
        categories: List[str] = None,
        keywords: List[str] = None,
        max_papers: int = 50,
        date_range: str = "1m"
    ) -> Dict:
        """
        Run complete ingestion pipeline
        
        Returns:
            Summary statistics
        """
        
        console.print(Panel.fit(
            "[bold blue]🧠 ArXiv Paper Ingestion Pipeline[/bold blue]\\n"
            "[dim]Downloading and processing research papers for ASI-ARCH[/dim]",
            style="blue"
        ))
        
        # Step 1: Search papers
        papers = self.search_papers(
            categories=categories,
            keywords=keywords, 
            max_results=max_papers,
            date_range=date_range
        )
        
        if not papers:
            console.print("❌ No papers found matching criteria")
            return {'papers_found': 0, 'papers_downloaded': 0, 'papers_ingested': 0}
        
        # Step 2: Download papers
        downloaded_papers = self.download_papers(papers)
        
        # Step 3: Ingest to Pixeltable
        ingested_count = self.ingest_papers_to_pixeltable(downloaded_papers)
        
        # Summary
        summary = {
            'papers_found': len(papers),
            'papers_downloaded': len([p for p in downloaded_papers if p.get('processing_status') == 'downloaded']),
            'papers_ingested': ingested_count,
            'categories': categories or ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE'],
            'date_range': date_range,
            'download_dir': str(self.data_dir)
        }
        
        self._display_summary(summary)
        return summary
    
    def get_papers_summary(self) -> Dict:
        """Get summary of papers currently in the database"""
        
        try:
            all_papers = self.papers_table.select().collect()
            
            if all_papers.empty:
                return {'total_papers': 0}
            
            # Calculate statistics
            total_papers = len(all_papers)
            categories = {}
            recent_papers = 0
            successful_downloads = 0
            
            for _, paper in all_papers.iterrows():
                # Count categories
                if paper['categories']:
                    for cat in paper['categories']:
                        categories[cat] = categories.get(cat, 0) + 1
                
                # Count recent papers (last 30 days)
                if paper['published_date'] and (datetime.now() - paper['published_date']).days <= 30:
                    recent_papers += 1
                
                # Count successful downloads
                if paper['processing_status'] == 'downloaded':
                    successful_downloads += 1
            
            return {
                'total_papers': total_papers,
                'successful_downloads': successful_downloads,
                'recent_papers': recent_papers,
                'top_categories': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]),
                'download_success_rate': successful_downloads / total_papers if total_papers > 0 else 0
            }
            
        except Exception as e:
            console.print(f"❌ Error getting papers summary: {e}")
            return {'total_papers': 0, 'error': str(e)}
    
    def _get_date_filter(self, date_range: str) -> Optional[datetime]:
        """Convert date range string to datetime filter"""
        
        range_map = {
            '1d': 1,
            '1w': 7, 
            '1m': 30,
            '3m': 90,
            '6m': 180
        }
        
        if date_range not in range_map:
            return None
        
        days_back = range_map[date_range]
        return datetime.now() - timedelta(days=days_back)
    
    def _calculate_relevance(self, paper) -> float:
        """Calculate relevance score for a paper based on AI/ML keywords"""
        
        ai_keywords = [
            'neural network', 'deep learning', 'machine learning', 'artificial intelligence',
            'transformer', 'attention', 'convolution', 'reinforcement learning',
            'generative', 'diffusion', 'language model', 'computer vision',
            'natural language processing', 'nlp', 'llm', 'gpt', 'bert'
        ]
        
        text = (paper.title + ' ' + paper.summary).lower()
        matches = sum(1 for keyword in ai_keywords if keyword in text)
        
        # Base score + keyword bonus + recency bonus
        base_score = 0.3
        keyword_score = min(matches * 0.1, 0.5)  # Max 0.5 for keywords
        recency_score = 0.2 if (datetime.now() - paper.published).days <= 30 else 0
        
        return min(base_score + keyword_score + recency_score, 1.0)
    
    def _display_summary(self, summary: Dict):
        """Display ingestion summary in a nice table"""
        
        table = Table(title="📊 ArXiv Ingestion Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Papers Found", str(summary['papers_found']))
        table.add_row("Papers Downloaded", str(summary['papers_downloaded']))
        table.add_row("Papers Ingested", str(summary['papers_ingested']))
        table.add_row("Categories", ", ".join(summary['categories']))
        table.add_row("Date Range", summary['date_range'])
        table.add_row("Download Directory", summary['download_dir'])
        
        console.print(table)
        
        # Success rate
        if summary['papers_found'] > 0:
            success_rate = summary['papers_ingested'] / summary['papers_found']
            if success_rate >= 0.8:
                console.print(f"\n🎉 [bold green]High success rate: {success_rate:.1%}[/bold green]")
            elif success_rate >= 0.5:
                console.print(f"\n✅ [bold yellow]Moderate success rate: {success_rate:.1%}[/bold yellow]")
            else:
                console.print(f"\n⚠️ [bold red]Low success rate: {success_rate:.1%}[/bold red]")


def main():
    """Command line interface for ArXiv ingestion"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python arxiv_ingestion.py <command>")
        print("Commands: search, download, ingest, summary")
        return
    
    system = ArXivIngestionSystem()
    command = sys.argv[1]
    
    if command == "search":
        papers = system.search_papers(max_results=10)
        for paper in papers[:5]:
            print(f"- {paper['title']} ({paper['arxiv_id']})")
    
    elif command == "ingest":
        system.run_full_ingestion(max_papers=20)
    
    elif command == "summary":
        summary = system.get_papers_summary()
        print(f"Total papers: {summary.get('total_papers', 0)}")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()