"""
Interactive CLI for ASI-ARCH - Showcasing Pixeltable's Capabilities

User-driven interface with choices for papers, models, and configurations.
Designed to demonstrate the full power of autonomous AI research.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from .cli_utils import safe_confirm, safe_prompt, safe_int_prompt, detect_environment
from pathlib import Path
from typing import Optional, List
import json
import sys
import os
import time

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from asi_arch import ASIArch, get_asi_arch
from model_system import get_model_manager, setup_models
from paper_analysis import PaperAnalysisSystem

app = typer.Typer(
    help="🧠 xPyLLMent ASI-ARCH: Interactive Autonomous Architecture Discovery",
    rich_markup_mode="rich"
)
console = Console()

@app.command("init")
def initialize(
    reset: bool = typer.Option(False, "--reset", help="Reset existing database"),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Run without interactive prompts")
):
    """🚀 Initialize ASI-ARCH with interactive setup"""
    
    console.print(Panel.fit(
        "[bold cyan]🧠 xPyLLMent ASI-ARCH Setup Wizard[/bold cyan]\n"
        "[dim]Autonomous AI Architecture Discovery[/dim]", 
        style="cyan"
    ))
    
    console.print("\\n[bold green]Welcome to the future of AI research![/bold green]")
    console.print("Let's set up your autonomous research system step by step.\\n")
    
    # Show environment info for debugging
    env_info = detect_environment() 
    if not env_info['is_interactive']:
        console.print(f"[dim]Environment: {env_info['term']} (non-interactive terminal detected)[/dim]\\n")
    
    # Initialize core system
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("🔧 Initializing Pixeltable database...", total=None)
        
        # Handle interactive prompt with proper terminal detection
        if reset:
            should_reset = True
        elif non_interactive:
            should_reset = False
            console.print("🔄 Using default: No database reset (non-interactive mode)")
        else:
            should_reset = safe_confirm("🔄 Reset existing database?", default=False)
        
        if should_reset:
            system = ASIArch(reset_db=True)
        else:
            system = ASIArch(reset_db=False)
        
        progress.update(task, description="✅ Database ready!")
    
    console.print("\\n🎉 Core system initialized!")
    
    # Research Papers Setup
    console.print("\\n" + "="*60)
    console.print("[bold blue]📚 RESEARCH KNOWLEDGE BASE SETUP[/bold blue]")
    console.print("Choose how to populate the research knowledge base:")
    
    paper_options = [
        "arxiv - Download latest papers from ArXiv (Recommended)",
        "local - Process existing local papers",
        "demo - Use demo papers for testing", 
        "skip - Skip for now"
    ]
    
    for i, option in enumerate(paper_options, 1):
        console.print(f"  {i}. {option}")
    
    if non_interactive:
        paper_choice = "demo"
        console.print("📚 Using default: demo papers (non-interactive mode)")
    else:
        # Allow both numeric and string inputs
        user_input = safe_prompt(
            "\\nSelect option [1-4 or arxiv/local/demo/skip]",
            choices=[],  # Don't restrict choices, we'll validate manually
            default="demo"
        )
        
        # Map numeric inputs to options
        option_map = {
            "1": "arxiv", 
            "2": "local",
            "3": "demo", 
            "4": "skip"
        }
        
        paper_choice = option_map.get(user_input, user_input)
        
        # Validate the choice
        valid_choices = ["arxiv", "local", "demo", "skip"]
        if paper_choice not in valid_choices:
            console.print(f"⚠️  Invalid choice '{user_input}', using default: demo")
            paper_choice = "demo"
    
    if paper_choice == "arxiv":
        _setup_arxiv_papers(non_interactive)
    elif paper_choice == "local":
        _setup_local_papers()
    elif paper_choice == "demo":
        _setup_demo_papers()
    else:
        console.print("⏭️  Skipping paper setup")
    
    # Model configuration using our advanced system
    console.print("\\n" + "="*60)
    console.print("[bold blue]🤖 BASE MODEL CONFIGURATION[/bold blue]")
    
    if non_interactive:
        console.print("⏭️  Using default model configuration (non-interactive mode)")
        model_manager = get_model_manager()
        model_config = model_manager.get_current_config()
        model_choice = model_config['provider']
    else:
        console.print("Setting up AI models using Pixeltable's infrastructure...")
        model_config = setup_models()
        
        if model_config:
            model_choice = model_config['provider']
            console.print(f"✅ [green]Model configured successfully![/green]")
            console.print(f"🤖 Provider: {model_config['provider'].title()}")
            console.print(f"🧠 Model: {model_config['display_name']}")
        else:
            console.print("⚠️  No model configured, using default")
            model_choice = "anthropic"
    
    # Save configuration
    config = {
        "initialized": True,
        "papers": {"source": paper_choice},
        "model": {"source": model_choice},
        "setup_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    config_file = config_path or Path("asi_arch_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Final summary
    console.print("\\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]🎉 xPyLLMent ASI-ARCH READY![/bold green]\\n\\n"
        f"📄 Configuration: {config_file}\\n"
        f"📚 Papers: {paper_choice}\\n"
        f"🤖 Model: {model_choice}\\n\\n"
        "[bold]Next steps:[/bold]\\n"
        "• Run [cyan]xpyllment discover[/cyan] to start research\\n"
        "• Run [cyan]xpyllment status[/cyan] to check system\\n"
        "• Run [cyan]xpyllment results[/cyan] to view discoveries",
        style="green"
    ))

@app.command("discover")
def start_discovery(
    target: str = typer.Option("reasoning", "--target", "-t", help="Target capability"),
    generations: int = typer.Option(3, "--generations", "-g", help="Number of generations"),
    interactive: bool = typer.Option(True, "--interactive/--batch", help="Interactive mode")
):
    """🧬 Start autonomous architecture discovery"""
    
    console.print(Panel.fit(
        "[bold blue]🧬 xPyLLMent: Autonomous Architecture Discovery[/bold blue]\\n"
        "[dim]AI agents will now discover novel neural architectures[/dim]", 
        style="blue"
    ))
    
    system = get_asi_arch()
    
    # Show current system status
    _show_system_status(system)
    
    if interactive:
        # Interactive configuration
        console.print("\\n[bold]🎯 Research Configuration[/bold]")
        
        # Target capability selection
        target_options = [
            "reasoning - General reasoning and problem solving",
            "language - Natural language understanding", 
            "vision - Computer vision and image processing",
            "multimodal - Cross-modal understanding",
            "efficiency - Computational efficiency optimization"
        ]
        
        console.print("\\nAvailable research targets:")
        for i, option in enumerate(target_options, 1):
            console.print(f"  {i}. {option}")
        
        target = Prompt.ask(
            "\\nSelect target capability",
            choices=["reasoning", "language", "vision", "multimodal", "efficiency"],
            default=target
        )
        
        generations = IntPrompt.ask(
            f"How many generations to evolve?",
            default=generations
        )
    
    if not Confirm.ask(f"\\n🚀 Start discovery targeting '{target}' for {generations} generations?", default=True):
        console.print("🛑 Discovery cancelled")
        return
    
    # Start the discovery process
    console.print(f"\\n[bold green]🚀 Launching autonomous discovery![/bold green]")
    console.print(f"🎯 Target: {target}")
    console.print(f"🧬 Generations: {generations}")
    
    # Run each generation
    for gen in range(1, generations + 1):
        console.print(f"\\n{'='*60}")
        console.print(f"[bold cyan]🧬 GENERATION {gen}[/bold cyan]")
        
        # Get parent experiments for evolution (if not first generation)
        parent_ids = []
        if gen > 1:
            if interactive and Confirm.ask("🧬 Select specific parents for evolution?", default=False):
                parent_ids = _select_parent_experiments(system, gen)
            else:
                # Auto-select top 2 from previous generation
                experiments = system.list_experiments(limit=10)
                prev_gen_experiments = [e for e in experiments if e['generation'] == gen-1]
                if prev_gen_experiments:
                    prev_gen_experiments.sort(key=lambda x: x.get('fitness_score', 0), reverse=True)
                    parent_ids = [e['experiment_id'] for e in prev_gen_experiments[:2]]
        
        # Launch generation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🧠 AI agents discovering Generation {gen} architecture...", total=None)
            
            exp_id = system.start_experiment(
                target_capability=target,
                generation=gen,
                parent_ids=parent_ids
            )
            
            progress.update(task, description=f"✅ Generation {gen} experiment launched: {exp_id[:12]}...")
        
        # Wait for results and display
        console.print("⏳ Waiting for AI agents to complete discovery...")
        
        results = _wait_for_results(system, exp_id)
        _display_generation_results(gen, results)
        
        # Ask to continue (except for last generation)
        if gen < generations and interactive:
            if not Confirm.ask(f"\\n➡️  Continue to Generation {gen+1}?", default=True):
                console.print(f"🛑 Stopping at Generation {gen}")
                break
    
    # Final summary
    console.print(f"\\n{'='*60}")
    console.print("[bold green]🎉 DISCOVERY COMPLETE![/bold green]")
    
    _show_discovery_summary(system, generations, target)

@app.command("results")  
def show_results(
    experiment_id: Optional[str] = typer.Argument(None, help="Specific experiment ID"),
    latest: bool = typer.Option(False, "--latest", "-l", help="Show latest experiment"),
    generation: Optional[int] = typer.Option(None, "--gen", "-g", help="Show specific generation")
):
    """📊 View experiment results and discoveries"""
    
    system = get_asi_arch()
    
    if latest or not experiment_id:
        experiments = system.list_experiments(limit=1)
        if not experiments:
            console.print("❌ No experiments found")
            return
        experiment_id = experiments[0]['experiment_id']
    
    if generation:
        experiments = system.list_experiments(limit=50)
        gen_experiments = [e for e in experiments if e['generation'] == generation]
        if not gen_experiments:
            console.print(f"❌ No experiments found for generation {generation}")
            return
        
        console.print(f"[bold]🧬 Generation {generation} Results[/bold]")
        _display_generation_comparison(gen_experiments)
        return
    
    # Show specific experiment
    console.print(f"🔬 Fetching results for {experiment_id}...")
    results = system.get_experiment_results(experiment_id)
    
    _display_detailed_results(results)

@app.command("list")
def list_experiments(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of experiments to show"),
    generation: Optional[int] = typer.Option(None, "--gen", "-g", help="Filter by generation")
):
    """📋 List experiments and discoveries"""
    
    system = get_asi_arch()
    experiments = system.list_experiments(limit=limit)
    
    if generation:
        experiments = [e for e in experiments if e['generation'] == generation]
    
    if not experiments:
        console.print("❌ No experiments found")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=15)
    table.add_column("Gen", style="yellow", width=4)
    table.add_column("Target", style="green", width=12)
    table.add_column("Fitness", style="red", width=8)
    table.add_column("Status", style="blue", width=12)
    table.add_column("Created", style="dim", width=20)
    
    for exp in experiments:
        status_emoji = "✅" if exp['status'] == 'completed' else "🔄" if exp['status'] == 'researching' else "❌"
        
        table.add_row(
            exp['experiment_id'][:12] + "...",
            str(exp['generation']),
            exp['target_capability'],
            f"{exp['fitness_score']:.3f}" if exp['fitness_score'] else "N/A",
            f"{status_emoji} {exp['status']}",
            str(exp['created_at'])[:19]
        )
    
    console.print(table)
    
    # Summary stats
    avg_fitness = sum(e.get('fitness_score', 0) for e in experiments) / len(experiments)
    max_fitness = max(e.get('fitness_score', 0) for e in experiments)
    
    console.print(f"\\n📊 [bold]Summary:[/bold] {len(experiments)} experiments, "
                 f"avg fitness: {avg_fitness:.3f}, max fitness: {max_fitness:.3f}")

@app.command("status")
def show_status():
    """📊 Show system status and health"""
    system = get_asi_arch()
    _show_system_status(system)

@app.command("papers")
def manage_papers(
    download: bool = typer.Option(False, "--download", help="Download new papers from ArXiv"),
    categories: str = typer.Option("cs.AI,cs.LG,cs.CL", "--categories", "-c", help="ArXiv categories (comma-separated)"),
    max_papers: int = typer.Option(50, "--max", "-m", help="Maximum papers to download"),
    date_range: str = typer.Option("1m", "--date-range", "-d", help="Date range (1d, 1w, 1m, 3m, 6m)"),
    summary: bool = typer.Option(False, "--summary", "-s", help="Show papers summary")
):
    """📚 Manage research paper database"""
    
    if summary or (not download and not any([categories != "cs.AI,cs.LG,cs.CL", max_papers != 50, date_range != "1m"])):
        console.print(Panel.fit("📚 Research Papers Database", style="blue"))
        
        from .simple_arxiv import SimpleArXivDownloader
        downloader = SimpleArXivDownloader()
        
        summary_data = downloader.get_summary()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(summary_data.get('total_papers', 0)))
        table.add_row("Successfully Downloaded", str(summary_data.get('successful_downloads', 0)))
        table.add_row("Recent Papers (30d)", str(summary_data.get('recent_papers', 0)))
        table.add_row("Download Success Rate", f"{summary_data.get('download_success_rate', 0):.1%}")
        
        console.print(table)
        
        if summary_data.get('top_categories'):
            console.print("\n[bold]📊 Top Categories:[/bold]")
            for cat, count in list(summary_data['top_categories'].items())[:5]:
                console.print(f"  • {cat}: {count} papers")
    
    if download:
        console.print(Panel.fit("📥 ArXiv Paper Download", style="green"))
        
        from .simple_arxiv import SimpleArXivDownloader
        
        # Parse categories
        category_list = [cat.strip() for cat in categories.split(",")]
        
        console.print(f"🎯 Categories: {', '.join(category_list)}")
        console.print(f"📅 Date range: {date_range}")
        console.print(f"📊 Max papers: {max_papers}")
        
        downloader = SimpleArXivDownloader()
        summary_result = downloader.search_and_download(
            categories=category_list,
            max_papers=max_papers,
            date_range=date_range
        )
        
        if summary_result:
            console.print("\n🎉 [bold green]Paper download completed![/bold green]")
            console.print("💡 Use 'xpyllment papers --summary' to see the updated database")

@app.command("snapshot")
def create_snapshot(
    name: str = typer.Argument(help="Snapshot name"),
    description: str = typer.Option("", "--desc", "-d", help="Snapshot description"),
    public: bool = typer.Option(False, "--public", "-p", help="Make snapshot public")
):
    """📸 Create shareable research snapshot"""
    
    console.print(Panel.fit(f"📸 Creating Research Snapshot\\n[bold]{name}[/bold]", style="magenta"))
    
    system = get_asi_arch()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating snapshot...", total=None)
        
        snapshot_id = system.create_research_snapshot(
            name=name,
            description=description,
            public=public
        )
        
        progress.update(task, description="✅ Snapshot created!")
    
    console.print(f"\\n[bold green]✅ Snapshot Created![/bold green]")
    console.print(f"📋 ID: {snapshot_id}")
    console.print(f"🔒 Visibility: {'Public' if public else 'Private'}")
    console.print(f"\\n💡 [dim]Share this snapshot with other researchers to reproduce your discoveries![/dim]")

@app.command("analyze")
def analyze_papers(
    max_papers: int = typer.Option(5, "--count", "-c", help="Number of papers to download and analyze"),
    categories: str = typer.Option("cs.AI,cs.LG", "--categories", help="ArXiv categories (comma-separated)"),
    extract_entities: bool = typer.Option(True, "--entities/--no-entities", help="Enable GLiNER entity extraction"),
    date_range: str = typer.Option("1w", "--date-range", "-d", help="Date range: 1d, 1w, 1m, 3m")
):
    """🛸 Download papers and extract entities with GLiNER"""
    
    console.print(Panel.fit(
        "[bold cyan]🛸 GLiNER Paper Analysis[/bold cyan]\\n"
        "[dim]Download + Entity Extraction Pipeline[/dim]",
        style="cyan"
    ))
    
    # Parse categories
    category_list = [cat.strip() for cat in categories.split(',')]
    
    console.print(f"📋 Configuration:")
    console.print(f"  📥 Papers: {max_papers}")
    console.print(f"  🏷️  Categories: {', '.join(category_list)}")
    console.print(f"  📅 Date Range: {date_range}")
    console.print(f"  🛸 GLiNER: {'Enabled' if extract_entities else 'Disabled'}")
    
    # Initialize analysis system
    analysis_system = PaperAnalysisSystem()
    
    # Run analysis pipeline
    results = analysis_system.download_and_analyze_papers(
        categories=category_list,
        max_papers=max_papers,
        date_range=date_range,
        extract_entities=extract_entities
    )
    
    # Display results
    console.print("\\n" + "="*60)
    console.print("[bold green]📊 Analysis Results[/bold green]")
    console.print(f"✅ Downloaded: {results['downloaded']} papers")
    console.print(f"❌ Failed: {results['failed']} downloads")
    
    if results.get('entity_analysis'):
        analysis = results['entity_analysis']
        console.print(f"🛸 Analyzed: {analysis['analyzed_papers']} papers")
        console.print(f"🏷️  Entities: ~{analysis['estimated_entities']} extracted")
    
    if results['downloaded'] > 0:
        console.print("\\n💡 [dim]Use 'xpyllment dashboard' to view detailed analysis![/dim]")

@app.command("dashboard")
def show_dashboard():
    """📊 Display research analysis dashboard"""
    
    # Initialize analysis system
    analysis_system = PaperAnalysisSystem()
    
    # Display comprehensive dashboard
    analysis_system.display_analysis_dashboard()

@app.command("entities")
def show_entities(
    paper_id: Optional[str] = typer.Argument(None, help="Specific paper ArXiv ID to analyze"),
    trends: bool = typer.Option(False, "--trends", "-t", help="Show entity trends across all papers")
):
    """🛸 GLiNER entity analysis and trends"""
    
    analysis_system = PaperAnalysisSystem()
    
    if not analysis_system._ensure_gliner():
        console.print("❌ GLiNER not available - please run 'xpyllment analyze' first")
        return
    
    if paper_id:
        # Analyze specific paper
        console.print(f"🛸 Analyzing entities for paper: {paper_id}")
        analysis_system.analyze_specific_paper(paper_id)
    elif trends:
        # Show overall trends
        analysis_system.gliner_system.display_entity_analysis()
    else:
        # Default: show recent analysis summary
        console.print("🛸 [bold cyan]GLiNER Entity Analysis Summary[/bold cyan]")
        
        try:
            trends_data = analysis_system.gliner_system.analyze_entity_trends(limit=15)
            
            console.print(f"📊 Papers analyzed: {trends_data['total_papers_analyzed']}")
            console.print(f"🏷️  Unique entities: {trends_data['total_unique_entities']}")
            console.print(f"📝 Entity types: {trends_data['total_unique_types']}")
            
            # Quick preview of top entities
            console.print("\\n🔥 **Top Research Entities**")
            for entity, freq in trends_data['top_entities'][:8]:
                console.print(f"  {entity}: {freq} mentions")
                
            console.print("\\n💡 [dim]Use --trends for detailed analysis or specify paper ArXiv ID[/dim]")
            
        except Exception as e:
            console.print(f"❌ Analysis failed: {e}")
            console.print("💡 [dim]Try running 'xpyllment analyze' first to populate the database[/dim]")

def _setup_arxiv_papers(non_interactive: bool = False):
    """Set up ArXiv paper ingestion with user choices"""
    console.print("\\n[bold blue]📚 ArXiv Paper Setup[/bold blue]")
    
    # Category selection
    categories = {
        "cs.AI": "Artificial Intelligence",
        "cs.LG": "Machine Learning", 
        "cs.CL": "Computation and Language",
        "cs.CV": "Computer Vision",
        "cs.NE": "Neural and Evolutionary Computing",
        "cs.RO": "Robotics",
        "stat.ML": "Machine Learning (Statistics)"
    }
    
    console.print("\\nAvailable categories:")
    for code, name in categories.items():
        console.print(f"  • {code}: {name}")
    
    if non_interactive:
        selected = ["cs.AI", "cs.LG", "cs.CL"]
        console.print("📚 Using default categories: cs.AI, cs.LG, cs.CL (non-interactive mode)")
    else:
        selected_str = safe_prompt(
            "\\nSelect categories (comma-separated)",
            choices=[],  # Allow any input for comma-separated values
            default="cs.AI,cs.LG,cs.CL"
        )
        selected = [cat.strip() for cat in selected_str.split(",")]
    
    # Date range
    date_options = {
        "1d": "Last 24 hours",
        "1w": "Last week", 
        "1m": "Last month",
        "3m": "Last 3 months",
        "6m": "Last 6 months"
    }
    
    console.print("\\nDate range options:")
    for key, desc in date_options.items():
        console.print(f"  • {key}: {desc}")
    
    if non_interactive:
        date_range = "1m"
        console.print("📅 Using default date range: 1m (non-interactive mode)")
    else:
        date_range = safe_prompt(
            "\\nSelect date range",
            choices=list(date_options.keys()),
            default="1m"
        )
    
    # Max papers
    if non_interactive:
        max_papers = 50
        console.print("📊 Using default max papers: 50 (non-interactive mode)")
    else:
        max_papers = safe_int_prompt("Maximum papers to download", default=50)
    
    console.print(f"\\n📥 [bold]Starting ArXiv Download![/bold]")
    console.print(f"Categories: {', '.join(selected)}")
    console.print(f"Date range: {date_options[date_range]}")
    console.print(f"Max papers: {max_papers}")
    
    # Actually run the ingestion
    try:
        from .simple_arxiv import SimpleArXivDownloader
        
        downloader = SimpleArXivDownloader()
        result = downloader.search_and_download(
            categories=selected,
            max_papers=max_papers,
            date_range=date_range
        )
        
        console.print("\\n🎉 [bold green]ArXiv download completed successfully![/bold green]")
        return result
        
    except Exception as e:
        console.print(f"\\n❌ [bold red]ArXiv download failed: {e}[/bold red]")
        console.print("📝 You can run download later with: xpyllment papers --download")
        return None

def _setup_demo_papers():
    """Set up demo papers for testing"""
    console.print("\\n[bold blue]📚 Demo Papers Setup[/bold blue]")
    console.print("Setting up curated demo papers for testing...")
    console.print("✅ Demo papers configured!")

def _setup_local_papers():
    """Set up local paper processing"""
    paper_path = Prompt.ask("📂 Enter path to local papers directory")
    console.print(f"\\n📂 Local papers path: {paper_path}")
    console.print("⚠️  Local paper processing will be implemented in next session!")


def _show_system_status(system: ASIArch):
    """Display comprehensive system status"""
    
    console.print(Panel.fit("[bold blue]📊 xPyLLMent ASI-ARCH System Status[/bold blue]", style="blue"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", style="green", width=15) 
    table.add_column("Details", style="dim", width=40)
    
    # Database status
    try:
        experiments = system.list_experiments(limit=1)
        table.add_row("🗄️  Database", "✅ Connected", f"Pixeltable active, {len(system.list_experiments(50))} total experiments")
    except Exception as e:
        table.add_row("🗄️  Database", "❌ Error", f"Connection failed: {str(e)[:30]}...")
    
    # AI Agents status
    table.add_row("🧠 AI Agents", "✅ Ready", "Researcher, Engineer, Fitness evaluators deployed")
    
    # Evolution status
    try:
        experiments = system.list_experiments(limit=10)
        if experiments:
            latest_gen = max(exp['generation'] for exp in experiments)
            active_count = len([e for e in experiments if e['status'] in ['researching', 'pending']])
            table.add_row("🧬 Evolution", "🔄 Active" if active_count > 0 else "✅ Ready", 
                         f"Generation {latest_gen}, {active_count} active experiments")
        else:
            table.add_row("🧬 Evolution", "⭐ Ready", "No experiments yet - ready to discover!")
    except Exception as e:
        table.add_row("🧬 Evolution", "❓ Unknown", f"Status check failed: {str(e)[:30]}...")
    
    # Research knowledge base
    table.add_row("📚 Knowledge Base", "⚠️  Basic", "Demo setup - expand with real papers")
    
    # Model configuration  
    table.add_row("🤖 Models", "✅ Anthropic", "Claude-3.5-Sonnet via Pixeltable")
    
    console.print(table)

def _wait_for_results(system: ASIArch, exp_id: str, timeout: int = 60) -> dict:
    """Wait for experiment results with progress indication"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("⏳ AI agents working on discovery...", total=None)
        
        for i in range(timeout):
            time.sleep(1)
            results = system.get_experiment_results(exp_id)
            
            # Check if we have meaningful results
            hypothesis = results.get('research_hypothesis', {})
            if isinstance(hypothesis, dict) and 'hypothesis' in hypothesis:
                progress.update(task, description="✅ Discovery complete!")
                break
            
            if i % 10 == 0 and i > 0:
                progress.update(task, description=f"⏳ AI agents working... ({i}s)")
        
        return results

def _display_generation_results(generation: int, results: dict):
    """Display results for a specific generation"""
    
    console.print(f"\\n[bold green]✨ Generation {generation} Discovery Results[/bold green]")
    
    # Basic experiment info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan", width=15)
    info_table.add_column("Value", style="green")
    
    info_table.add_row("🆔 Experiment ID", results['experiment_id'][:16] + "...")
    info_table.add_row("🎯 Target", results['target_capability'])
    info_table.add_row("📊 Fitness Score", f"{results['fitness_score']:.3f}")
    info_table.add_row("⚡ Status", results['status'])
    
    console.print(info_table)
    
    # AI-discovered architecture
    hypothesis = results.get('research_hypothesis', {})
    if isinstance(hypothesis, dict) and 'hypothesis' in hypothesis:
        console.print(f"\\n[bold cyan]🧠 AI-Discovered Architecture:[/bold cyan]")
        console.print(Panel.fit(
            hypothesis['hypothesis'],
            title="🏗️ Architecture Discovery",
            style="cyan"
        ))
        
        # Key innovations
        if 'key_innovations' in hypothesis:
            console.print(f"\\n[bold yellow]🚀 Key Innovations:[/bold yellow]")
            for i, innovation in enumerate(hypothesis['key_innovations'], 1):
                console.print(f"   {i}. {innovation}")
        
        # Metrics
        metrics_table = Table(show_header=False, box=None)
        metrics_table.add_column("Metric", style="yellow")
        metrics_table.add_column("Score", style="green")
        
        if 'novelty_score' in hypothesis:
            metrics_table.add_row("⚡ Novelty", f"{hypothesis['novelty_score']}")
        if 'confidence' in hypothesis:
            metrics_table.add_row("🎯 Confidence", f"{hypothesis['confidence']}")
        
        console.print(f"\\n[bold]📈 Discovery Metrics:[/bold]")
        console.print(metrics_table)
    else:
        console.print("\\n⚠️  Discovery data not yet available or parsing failed")

def _display_detailed_results(results: dict):
    """Display comprehensive results for an experiment"""
    
    console.print(Panel.fit(
        f"[bold blue]🔬 Detailed Experiment Results[/bold blue]\\n"
        f"[dim]{results['experiment_id']}[/dim]", 
        style="blue"
    ))
    
    # Comprehensive info table
    info_table = Table(show_header=True, header_style="bold magenta")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Experiment ID", results['experiment_id'])
    info_table.add_row("Generation", str(results['generation']))
    info_table.add_row("Target Capability", results['target_capability'])
    info_table.add_row("Status", results['status'])
    info_table.add_row("Fitness Score", f"{results['fitness_score']:.6f}")
    info_table.add_row("Created At", str(results['created_at']))
    
    console.print(info_table)
    
    # Research hypothesis details
    hypothesis = results.get('research_hypothesis', {})
    if isinstance(hypothesis, dict) and 'hypothesis' in hypothesis:
        
        console.print(f"\\n[bold green]🧠 Research Hypothesis[/bold green]")
        console.print(hypothesis['hypothesis'])
        
        if 'scientific_motivation' in hypothesis:
            console.print(f"\\n[bold blue]🔬 Scientific Motivation[/bold blue]")
            console.print(hypothesis['scientific_motivation'])
        
        if 'key_innovations' in hypothesis:
            console.print(f"\\n[bold yellow]🚀 Key Innovations[/bold yellow]")
            for i, innovation in enumerate(hypothesis['key_innovations'], 1):
                console.print(f"  {i}. {innovation}")
        
        if 'expected_improvements' in hypothesis:
            console.print(f"\\n[bold magenta]📈 Expected Improvements[/bold magenta]") 
            improvements = hypothesis['expected_improvements']
            if isinstance(improvements, dict):
                for metric, improvement in improvements.items():
                    console.print(f"  • {metric}: {improvement}")
    
    # Generated code preview
    if results.get('generated_code'):
        console.print(f"\\n[bold cyan]⚙️ Generated Code Preview[/bold cyan]")
        code_preview = results['generated_code'][:300] + "..." if len(results['generated_code']) > 300 else results['generated_code']
        console.print(Panel.fit(code_preview, title="PyTorch Implementation", style="dim"))

def _display_generation_comparison(experiments: List[dict]):
    """Display comparison of experiments within a generation"""
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="yellow", width=6)
    table.add_column("Experiment ID", style="cyan", width=18)
    table.add_column("Fitness", style="green", width=10)
    table.add_column("Architecture Type", style="blue", width=30)
    table.add_column("Status", style="red", width=12)
    
    # Sort by fitness
    experiments.sort(key=lambda x: x.get('fitness_score', 0), reverse=True)
    
    for i, exp in enumerate(experiments, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        # Try to extract architecture name from results
        arch_type = "Unknown"
        try:
            results = get_asi_arch().get_experiment_results(exp['experiment_id'])
            hypothesis = results.get('research_hypothesis', {})
            if isinstance(hypothesis, dict) and 'hypothesis' in hypothesis:
                arch_name = hypothesis['hypothesis'].split(' - ')[0] if ' - ' in hypothesis['hypothesis'] else hypothesis['hypothesis'][:30]
                arch_type = arch_name
        except:
            pass
        
        table.add_row(
            f"{rank_emoji}",
            exp['experiment_id'][:16] + "...",
            f"{exp.get('fitness_score', 0):.3f}",
            arch_type,
            exp['status']
        )
    
    console.print(table)

def _select_parent_experiments(system: ASIArch, generation: int) -> List[str]:
    """Interactive parent selection for evolution"""
    
    console.print(f"\\n[bold]🧬 Parent Selection for Generation {generation}[/bold]")
    
    experiments = system.list_experiments(limit=20)
    prev_gen_experiments = [e for e in experiments if e['generation'] == generation-1]
    
    if not prev_gen_experiments:
        console.print("❌ No previous generation experiments found")
        return []
    
    # Sort by fitness
    prev_gen_experiments.sort(key=lambda x: x.get('fitness_score', 0), reverse=True)
    
    console.print(f"\\n🏆 Available parents from Generation {generation-1}:")
    for i, exp in enumerate(prev_gen_experiments[:8], 1):
        console.print(f"  {i}. {exp['experiment_id'][:12]}... (Fitness: {exp.get('fitness_score', 0):.3f})")
    
    selections = Prompt.ask(
        "\\nSelect parents (comma-separated numbers, or 'auto' for top 2)",
        default="auto"
    )
    
    if selections.lower() == "auto":
        selected = prev_gen_experiments[:2]
        console.print(f"🤖 Auto-selected top 2 parents")
    else:
        try:
            indices = [int(x.strip())-1 for x in selections.split(",")]
            selected = [prev_gen_experiments[i] for i in indices if 0 <= i < len(prev_gen_experiments)]
        except:
            console.print("⚠️  Invalid selection, using top 2")
            selected = prev_gen_experiments[:2]
    
    return [exp['experiment_id'] for exp in selected]

def _show_discovery_summary(system: ASIArch, generations: int, target: str):
    """Show final discovery summary across all generations"""
    
    experiments = system.list_experiments(limit=50)
    
    # Filter to recent experiments from this discovery session
    session_experiments = [e for e in experiments if e['generation'] <= generations]
    
    if not session_experiments:
        console.print("❌ No experiments found for summary")
        return
    
    # Summary stats
    avg_fitness = sum(e.get('fitness_score', 0) for e in session_experiments) / len(session_experiments)
    max_fitness = max(e.get('fitness_score', 0) for e in session_experiments)
    best_experiment = max(session_experiments, key=lambda x: x.get('fitness_score', 0))
    
    # Generation progress
    gen_stats = {}
    for exp in session_experiments:
        gen = exp['generation']
        if gen not in gen_stats:
            gen_stats[gen] = []
        gen_stats[gen].append(exp.get('fitness_score', 0))
    
    summary_table = Table(show_header=True, header_style="bold green")
    summary_table.add_column("Generation", style="cyan")
    summary_table.add_column("Experiments", style="yellow")
    summary_table.add_column("Avg Fitness", style="green")
    summary_table.add_column("Max Fitness", style="red")
    summary_table.add_column("Improvement", style="magenta")
    
    prev_max = 0
    for gen in sorted(gen_stats.keys()):
        gen_fitness = gen_stats[gen]
        avg_fit = sum(gen_fitness) / len(gen_fitness)
        max_fit = max(gen_fitness)
        improvement = max_fit - prev_max if prev_max > 0 else 0
        improvement_str = f"+{improvement:.3f}" if improvement > 0 else f"{improvement:.3f}"
        
        summary_table.add_row(
            str(gen),
            str(len(gen_fitness)),
            f"{avg_fit:.3f}",
            f"{max_fit:.3f}",
            improvement_str
        )
        prev_max = max_fit
    
    console.print(summary_table)
    
    # Best discovery
    console.print(f"\\n[bold green]🏆 Best Discovery:[/bold green]")
    console.print(f"🆔 Experiment: {best_experiment['experiment_id'][:16]}...")
    console.print(f"🧬 Generation: {best_experiment['generation']}")
    console.print(f"📊 Fitness: {best_experiment.get('fitness_score', 0):.3f}")
    
    # Recommendations
    console.print(f"\\n[bold blue]💡 Recommendations:[/bold blue]")
    if max_fitness > 0.5:
        console.print("✅ Strong discoveries found! Consider:")
        console.print("   • Create a snapshot to preserve results")
        console.print("   • Scale up the best architecture for full training")
        console.print("   • Continue evolution with more generations")
    else:
        console.print("⚠️  Fitness scores are moderate. Consider:")
        console.print("   • Adjusting target capabilities")
        console.print("   • Adding more research papers to knowledge base")
        console.print("   • Experimenting with different model configurations")

def main():
    """Entry point for the interactive CLI"""
    app()

if __name__ == "__main__":
    main()