"""
Simplified ArXiv paper download system
Focuses on download functionality without complex database schema
"""

import arxiv
import requests
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

class SimpleArXivDownloader:
    """Simple ArXiv paper downloader without database complexity"""
    
    def __init__(self, download_dir: Path = None):
        self.download_dir = download_dir or Path.home() / '.pixeltable' / 'arxiv_papers'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a simple JSON manifest to track downloads
        self.manifest_file = self.download_dir / 'manifest.json'
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load or create download manifest"""
        if self.manifest_file.exists():
            import json
            try:
                with open(self.manifest_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'papers': [], 'last_updated': None}
    
    def _save_manifest(self):
        """Save download manifest"""
        import json
        self.manifest['last_updated'] = datetime.now().isoformat()
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2, default=str)
    
    def search_and_download(
        self,
        categories: List[str] = None,
        max_papers: int = 20,
        date_range: str = "1m"
    ) -> Dict:
        """Search and download papers in one step"""
        
        if not categories:
            categories = ['cs.AI', 'cs.LG', 'cs.CL']
        
        console.print(Panel.fit(
            f"📥 ArXiv Paper Download\\n"
            f"[dim]Categories: {', '.join(categories)}\\n"
            f"Max papers: {max_papers}\\n"
            f"Date range: {date_range}[/dim]",
            style="blue"
        ))
        
        # Build search query
        category_query = ' OR '.join([f'cat:{cat}' for cat in categories])
        
        # Calculate date filter
        date_filter = self._get_date_filter(date_range)
        
        console.print(f"🔍 Searching ArXiv...")
        
        # Search ArXiv using the new API
        client = arxiv.Client()
        search = arxiv.Search(
            query=category_query,
            max_results=max_papers * 2,  # Get extra in case some fail
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        # Collect papers
        papers = []
        found_count = 0
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            search_task = progress.add_task("Fetching papers from ArXiv...", total=max_papers)
            
            for result in client.results(search):
                if found_count >= max_papers:
                    break
                
                # Filter by date if specified  
                if date_filter and result.published.replace(tzinfo=None) < date_filter:
                    continue
                
                # Check if already downloaded
                arxiv_id = result.entry_id.split('/')[-1]
                if any(p['arxiv_id'] == arxiv_id for p in self.manifest['papers']):
                    continue
                
                paper_data = {
                    'arxiv_id': arxiv_id,
                    'title': result.title,
                    'abstract': result.summary,
                    'authors': [author.name for author in result.authors],
                    'categories': result.categories,
                    'published_date': result.published.isoformat(),
                    'pdf_url': result.pdf_url,
                    'relevance_score': self._calculate_relevance(result)
                }
                
                papers.append(paper_data)
                found_count += 1
                progress.update(search_task, advance=1)
        
        if not papers:
            console.print("❌ No new papers found matching criteria")
            return {'downloaded': 0, 'failed': 0}
        
        console.print(f"✅ Found {len(papers)} new papers")
        
        # Download papers
        return self._download_papers(papers)
    
    def _download_papers(self, papers: List[Dict]) -> Dict:
        """Download PDF files for papers"""
        
        downloaded_count = 0
        failed_count = 0
        
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
                    progress.update(download_task, description=f"Downloading {paper['arxiv_id']}...")
                    
                    # Create safe filename
                    safe_title = "".join(c for c in paper['title'][:30] if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"{paper['arxiv_id'].replace('/', '_')}_{safe_title}.pdf"
                    file_path = self.download_dir / filename
                    
                    # Skip if already exists
                    if file_path.exists():
                        paper['pdf_path'] = str(file_path)
                        paper['file_size'] = file_path.stat().st_size
                        paper['download_date'] = datetime.now().isoformat()
                        paper['status'] = 'downloaded'
                        self.manifest['papers'].append(paper)
                        downloaded_count += 1
                        progress.update(download_task, advance=1)
                        continue
                    
                    # Download PDF
                    response = requests.get(paper['pdf_url'], stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Update paper info
                    paper['pdf_path'] = str(file_path)
                    paper['file_size'] = file_path.stat().st_size
                    paper['download_date'] = datetime.now().isoformat()
                    paper['status'] = 'downloaded'
                    
                    self.manifest['papers'].append(paper)
                    downloaded_count += 1
                    
                except Exception as e:
                    console.print(f"❌ Failed to download {paper['arxiv_id']}: {e}")
                    paper['status'] = 'failed'
                    paper['error'] = str(e)
                    failed_count += 1
                
                progress.update(download_task, advance=1)
        
        # Save manifest
        self._save_manifest()
        
        # Display results
        self._display_download_summary(downloaded_count, failed_count)
        
        return {
            'downloaded': downloaded_count,
            'failed': failed_count,
            'total_papers': len(self.manifest['papers'])
        }
    
    def get_summary(self) -> Dict:
        """Get download summary"""
        
        if not self.manifest['papers']:
            return {'total_papers': 0}
        
        # Calculate statistics
        total_papers = len(self.manifest['papers'])
        successful_downloads = len([p for p in self.manifest['papers'] if p.get('status') == 'downloaded'])
        
        # Recent papers (last 30 days)
        recent_papers = 0
        categories = {}
        total_size = 0
        
        for paper in self.manifest['papers']:
            # Count categories
            if paper.get('categories'):
                for cat in paper['categories']:
                    categories[cat] = categories.get(cat, 0) + 1
            
            # Count recent papers
            try:
                pub_date = datetime.fromisoformat(paper['published_date'].replace('Z', '+00:00'))
                if (datetime.now() - pub_date.replace(tzinfo=None)).days <= 30:
                    recent_papers += 1
            except:
                pass
            
            # Total file size
            if paper.get('file_size'):
                total_size += paper['file_size']
        
        return {
            'total_papers': total_papers,
            'successful_downloads': successful_downloads,
            'recent_papers': recent_papers,
            'top_categories': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]),
            'total_size_mb': total_size / (1024 * 1024),
            'download_directory': str(self.download_dir)
        }
    
    def _get_date_filter(self, date_range: str):
        """Convert date range string to datetime filter"""
        range_map = {'1d': 1, '1w': 7, '1m': 30, '3m': 90, '6m': 180}
        
        if date_range not in range_map:
            return None
        
        days_back = range_map[date_range]
        return datetime.now() - timedelta(days=days_back)
    
    def _calculate_relevance(self, paper) -> float:
        """Calculate relevance score based on AI/ML keywords"""
        ai_keywords = [
            'neural network', 'deep learning', 'machine learning', 'artificial intelligence',
            'transformer', 'attention', 'convolution', 'reinforcement learning',
            'generative', 'diffusion', 'language model', 'computer vision', 'llm'
        ]
        
        text = (paper.title + ' ' + paper.summary).lower()
        matches = sum(1 for keyword in ai_keywords if keyword in text)
        
        base_score = 0.3
        keyword_score = min(matches * 0.1, 0.5)
        recency_score = 0.2 if (datetime.now() - paper.published.replace(tzinfo=None)).days <= 30 else 0
        
        return min(base_score + keyword_score + recency_score, 1.0)
    
    def _display_download_summary(self, downloaded: int, failed: int):
        """Display download summary"""
        
        table = Table(title="📊 Download Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Successfully Downloaded", str(downloaded))
        table.add_row("Failed Downloads", str(failed))
        table.add_row("Success Rate", f"{downloaded/(downloaded+failed)*100:.1f}%" if (downloaded+failed) > 0 else "N/A")
        table.add_row("Download Directory", str(self.download_dir))
        
        console.print(table)
        
        if downloaded > 0:
            console.print(f"\n🎉 [bold green]Successfully downloaded {downloaded} papers![/bold green]")
        
        if failed > 0:
            console.print(f"⚠️ [bold yellow]{failed} downloads failed[/bold yellow]")


# CLI interface
def main():
    """Command line interface"""
    import sys
    
    downloader = SimpleArXivDownloader()
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        summary = downloader.get_summary()
        console.print(f"📚 Total papers: {summary['total_papers']}")
        console.print(f"💾 Total size: {summary['total_size_mb']:.1f} MB")
        console.print(f"📁 Directory: {summary['download_directory']}")
    else:
        # Default: download some papers
        result = downloader.search_and_download(
            categories=['cs.AI', 'cs.LG'],
            max_papers=5,
            date_range='1w'
        )
        console.print(f"\n✅ Download complete: {result['downloaded']} papers")


if __name__ == "__main__":
    main()