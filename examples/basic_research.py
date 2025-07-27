"""
Example: Basic Research Session

This example shows how to run a basic ASI-ARCH research session
to discover novel neural architectures autonomously.
"""

import asyncio
import logging
from pathlib import Path

import xpyllment


async def basic_research_example():
    """Run a basic research session"""
    
    print("🚀 Starting ASI-ARCH Research Session")
    print("=====================================")
    
    # Create research system
    print("\n📋 Initializing research system...")
    system = xpyllment.create_research_system()
    
    try:
        # Initialize all components
        await system.initialize()
        print("✅ System initialized successfully")
        
        # Show initial status
        status = system.get_system_status()
        print(f"\n📊 Initial Status:")
        print(f"   Population size: {status.get('population_size', 0)}")
        print(f"   Best fitness: {status.get('best_fitness', 0):.3f}")
        print(f"   Total experiments: {status.get('total_experiments', 0)}")
        
        # Run research for a few generations
        print(f"\n🧬 Starting evolutionary research...")
        print(f"   Generations: 3")
        print(f"   Experiments per generation: 2")
        print(f"   Total experiments planned: 6")
        
        await system.run_research_loop(
            max_generations=3,
            experiments_per_generation=2
        )
        
        # Show final results
        final_status = system.get_system_status()
        print(f"\n🎉 Research session completed!")
        print(f"   Total experiments: {final_status['total_experiments']}")
        print(f"   Successful experiments: {final_status['successful_experiments']}")
        print(f"   Success rate: {final_status['success_rate']:.1%}")
        print(f"   Best fitness achieved: {final_status.get('best_fitness', 0):.3f}")
        print(f"   Final generation: {final_status.get('generation', 0)}")
        
        # Create a snapshot for reproducibility
        if final_status['successful_experiments'] > 0:
            print(f"\n📸 Creating research snapshot...")
            snapshot_id = system.create_research_snapshot(
                "basic_example_session",
                "Results from basic research example"
            )
            print(f"   Snapshot created: {snapshot_id}")
        
        print(f"\n✨ Research session complete!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Research interrupted by user")
        system.stop_research()
        
    except Exception as e:
        print(f"\n❌ Research failed: {e}")
        raise
        
    finally:
        # Clean shutdown
        await system.shutdown()
        print(f"🔌 System shutdown complete")


async def configuration_example():
    """Example of custom configuration"""
    
    print("\n🔧 Configuration Example")
    print("========================")
    
    # Load default config
    config = xpyllment.load_config()
    
    # Modify evolution parameters for faster experimentation
    config.evolution.population_size = 20
    config.evolution.elite_size = 5
    config.evolution.mutation_rate = 0.2
    
    # Modify training for quick iterations
    config.training.max_steps = 1000
    config.training.batch_size = 16
    
    # Show configuration
    print(f"Population size: {config.evolution.population_size}")
    print(f"Elite size: {config.evolution.elite_size}")
    print(f"Training steps: {config.training.max_steps}")
    print(f"LLM provider: {config.llm.provider}")
    print(f"LLM model: {config.llm.model}")


def version_example():
    """Show version and system information"""
    
    print("\n📦 Version Information")
    print("======================")
    
    version_info = xpyllment.version_info()
    
    for key, value in version_info.items():
        if key == "dependencies":
            print(f"{key}:")
            for dep in value:
                print(f"  - {dep}")
        else:
            print(f"{key}: {value}")


async def main():
    """Main example runner"""
    
    print("🧠 xPyLLMent Examples")
    print("===================")
    
    # Show version info
    version_example()
    
    # Show configuration example
    await configuration_example()
    
    # Run basic research (commented out to avoid long runtime in example)
    print(f"\n⚠️  Note: Uncomment the line below to run actual research")
    print(f"This will take significant time and requires API keys")
    
    # Uncomment to run actual research:
    # await basic_research_example()
    
    print(f"\n✅ Examples complete!")


if __name__ == "__main__":
    # Set up logging for examples
    logging.basicConfig(level=logging.INFO)
    
    # Run examples
    asyncio.run(main())
