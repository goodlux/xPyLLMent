"""
Command Line Interface for xPyLLMent

Provides easy access to ASI-ARCH research functionality through CLI commands.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
import time

from .core import create_research_system
from .config import create_default_config, load_config


console = Console()


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """xPyLLMent ASI-ARCH Research System - Autonomous Architecture Discovery"""
    
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = Path(config) if config else None


@cli.command()
@click.option('--config-path', '-c', type=click.Path(), default='config.yaml', help='Configuration file path')
def init(config_path):
    """Initialize a new ASI-ARCH research project"""
    
    config_path = Path(config_path)
    
    if config_path.exists():
        if not click.confirm(f"Configuration file {config_path} already exists. Overwrite?"):
            console.print("[yellow]Initialization cancelled[/yellow]")
            return
    
    # Create default configuration
    console.print("[blue]Creating default configuration...[/blue]")
    config = create_default_config(config_path)
    
    console.print(f"[green]✓[/green] Configuration created at {config_path}")
    console.print("\n[blue]Configuration Summary:[/blue]")
    
    # Display config summary
    table = Table(title="ASI-ARCH Configuration")
    table.add_column("Component", style="cyan")
    table.add_column("Setting", style="magenta")
    table.add_column("Value", style="green")
    
    table.add_row("Database", "Host", config.database.host)
    table.add_row("Database", "Name", config.database.name)
    table.add_row("LLM", "Provider", config.llm.provider)
    table.add_row("LLM", "Model", config.llm.model)
    table.add_row("Evolution", "Population Size", str(config.evolution.population_size))
    table.add_row("Training", "Max Steps", str(config.training.max_steps))
    
    console.print(table)
    
    console.print(f"\n[blue]Next steps:[/blue]")
    console.print("1. Review and edit the configuration file if needed")
    console.print("2. Set up your API keys in environment variables")
    console.print("3. Run [cyan]xpyllment start[/cyan] to begin research")


@cli.command()
@click.option('--generations', '-g', default=10, help='Number of generations to evolve')
@click.option('--experiments', '-e', default=5, help='Experiments per generation')
@click.option('--daemon', '-d', is_flag=True, help='Run in daemon mode')
@click.pass_context
def start(ctx, generations, experiments, daemon):
    """Start the ASI-ARCH research loop"""
    
    config_path = ctx.obj.get('config_path')
    
    console.print(Panel.fit(
        "[bold blue]ASI-ARCH Research System[/bold blue]\n"
        "Autonomous Architecture Discovery",
        border_style="blue"
    ))
    
    async def run_research():
        try:
            # Create and initialize system
            with console.status("[blue]Initializing research system...[/blue]"):
                system = create_research_system(config_path)
                await system.initialize()
            
            console.print("[green]✓[/green] Research system initialized")
            
            # Display initial status
            status = system.get_system_status()
            _display_status(status)
            
            # Start research loop
            console.print(f"\n[blue]Starting research loop:[/blue]")
            console.print(f"  Generations: {generations}")
            console.print(f"  Experiments per generation: {experiments}")
            console.print(f"  Total experiments planned: {generations * experiments}")
            
            if not click.confirm("\nProceed with research?"):
                console.print("[yellow]Research cancelled[/yellow]")
                return
            
            # Run research with progress tracking
            if daemon:
                await _run_daemon_mode(system, generations, experiments)
            else:
                await _run_interactive_mode(system, generations, experiments)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Research interrupted by user[/yellow]")
            if 'system' in locals():
                system.stop_research()
        except Exception as e:
            console.print(f"[red]Research failed: {e}[/red]")
            sys.exit(1)
        finally:
            if 'system' in locals():
                await system.shutdown()
    
    # Run the async function
    asyncio.run(run_research())


async def _run_interactive_mode(system, generations, experiments):
    """Run research in interactive mode with live updates"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Running research...", total=generations)
        
        # Create a background task for the research loop
        research_task = asyncio.create_task(
            system.run_research_loop(generations, experiments)
        )
        
        # Monitor progress
        while not research_task.done():
            await asyncio.sleep(2)  # Update every 2 seconds
            
            status = system.get_system_status()
            current_gen = status.get('generation', 0)
            
            progress.update(
                task, 
                completed=current_gen,
                description=f"Generation {current_gen}/{generations} "
                           f"(Success rate: {status.get('success_rate', 0):.1%})"
            )
        
        # Wait for completion
        await research_task
        
        # Final status
        final_status = system.get_system_status()
        _display_final_results(final_status)


async def _run_daemon_mode(system, generations, experiments):
    """Run research in daemon mode with periodic status updates"""
    
    console.print("[blue]Running in daemon mode...[/blue]")
    console.print("Press Ctrl+C to stop gracefully")
    
    # Start research loop
    research_task = asyncio.create_task(
        system.run_research_loop(generations, experiments)
    )
    
    # Periodic status updates
    last_update = time.time()
    
    while not research_task.done():
        await asyncio.sleep(10)  # Check every 10 seconds
        
        # Update status every minute
        if time.time() - last_update > 60:
            status = system.get_system_status()
            console.print(f"\n[blue]Status Update:[/blue]")
            console.print(f"Generation: {status.get('generation', 0)}")
            console.print(f"Total experiments: {status.get('total_experiments', 0)}")
            console.print(f"Success rate: {status.get('success_rate', 0):.1%}")
            console.print(f"Best fitness: {status.get('best_fitness', 0):.3f}")
            last_update = time.time()
    
    # Wait for completion
    await research_task
    
    # Final results
    final_status = system.get_system_status()
    _display_final_results(final_status)


@cli.command()
@click.pass_context  
def status(ctx):
    """Show current research system status"""
    
    config_path = ctx.obj.get('config_path')
    
    async def get_status():
        try:
            system = create_research_system(config_path)
            await system.initialize()
            
            status = system.get_system_status()
            _display_status(status)
            
            await system.shutdown()
            
        except Exception as e:
            console.print(f"[red]Failed to get status: {e}[/red]")
    
    asyncio.run(get_status())


@cli.command()
@click.option('--name', '-n', required=True, help='Snapshot name')
@click.option('--description', '-d', default='', help='Snapshot description')
@click.pass_context
def snapshot(ctx, name, description):
    """Create a research snapshot for reproducibility"""
    
    config_path = ctx.obj.get('config_path')
    
    async def create_snapshot():
        try:
            system = create_research_system(config_path)
            await system.initialize()
            
            with console.status(f"[blue]Creating snapshot '{name}'...[/blue]"):
                snapshot_id = system.create_research_snapshot(name, description)
            
            console.print(f"[green]✓[/green] Snapshot created: {snapshot_id}")
            
            await system.shutdown()
            
        except Exception as e:
            console.print(f"[red]Failed to create snapshot: {e}[/red]")
    
    asyncio.run(create_snapshot())


@cli.command()
def config():
    """Show current configuration"""
    
    try:
        config = load_config()
        
        console.print("[blue]Current Configuration:[/blue]")
        
        # Create config display table
        table = Table(title="ASI-ARCH Configuration")
        table.add_column("Component", style="cyan")
        table.add_column("Setting", style="magenta")
        table.add_column("Value", style="green")
        
        # Database config
        table.add_row("Database", "Host", config.database.host)
        table.add_row("Database", "Port", str(config.database.port))
        table.add_row("Database", "Name", config.database.name)
        table.add_row("Database", "User", config.database.user)
        
        # LLM config
        table.add_row("LLM", "Provider", config.llm.provider)
        table.add_row("LLM", "Model", config.llm.model)
        table.add_row("LLM", "Max Tokens", str(config.llm.max_tokens))
        table.add_row("LLM", "Temperature", str(config.llm.temperature))
        
        # Evolution config
        table.add_row("Evolution", "Population Size", str(config.evolution.population_size))
        table.add_row("Evolution", "Elite Size", str(config.evolution.elite_size))
        table.add_row("Evolution", "Mutation Rate", str(config.evolution.mutation_rate))
        
        # Training config
        table.add_row("Training", "Batch Size", str(config.training.batch_size))
        table.add_row("Training", "Learning Rate", str(config.training.learning_rate))
        table.add_row("Training", "Max Steps", str(config.training.max_steps))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Failed to load configuration: {e}[/red]")


def _display_status(status: dict):
    """Display system status in a formatted table"""
    
    table = Table(title="System Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Initialized", "✓" if status['initialized'] else "✗")
    table.add_row("Research Active", "✓" if status['research_active'] else "✗")
    table.add_row("Total Experiments", str(status['total_experiments']))
    table.add_row("Successful Experiments", str(status['successful_experiments']))
    table.add_row("Success Rate", f"{status['success_rate']:.1%}")
    
    if 'generation' in status:
        table.add_row("Current Generation", str(status['generation']))
        table.add_row("Population Size", str(status.get('population_size', 0)))
        table.add_row("Best Fitness", f"{status.get('best_fitness', 0):.3f}")
        table.add_row("Average Fitness", f"{status.get('average_fitness', 0):.3f}")
        table.add_row("Diversity Index", f"{status.get('diversity_metrics', {}).get('diversity_index', 0):.3f}")
    
    console.print(table)


def _display_final_results(status: dict):
    """Display final research results"""
    
    console.print("\n[green]Research completed![/green]")
    
    # Results summary
    results_panel = Panel.fit(
        f"[bold]Final Results[/bold]\n\n"
        f"Total Experiments: {status['total_experiments']}\n"
        f"Successful: {status['successful_experiments']}\n"
        f"Success Rate: {status['success_rate']:.1%}\n"
        f"Best Fitness: {status.get('best_fitness', 0):.3f}\n"
        f"Final Generation: {status.get('generation', 0)}",
        border_style="green"
    )
    
    console.print(results_panel)
    
    # Recommendations
    if status['successful_experiments'] > 0:
        console.print("\n[blue]Next steps:[/blue]")
        console.print("• Review top-performing architectures in the database")
        console.print("• Create a snapshot to preserve your research")
        console.print("• Consider scaling up successful architectures")
    else:
        console.print("\n[yellow]No successful experiments found.[/yellow]")
        console.print("Consider adjusting:")
        console.print("• Evolution parameters (mutation rate, selection pressure)")
        console.print("• Training configuration (learning rate, max steps)")
        console.print("• Fitness function weights")


def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main()
