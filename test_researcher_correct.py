#!/usr/bin/env python3
"""
Test ASI-ARCH Researcher Agent with correct Pixeltable patterns
"""

import pixeltable as pxt
import json

def test_researcher_agent():
    """Test researcher agent using proper Pixeltable patterns"""
    
    pxt.init()
    
    # Clean up any existing test data
    if 'asi_arch_test' in pxt.list_dirs():
        pxt.drop_dir('asi_arch_test', force=True)
    
    # Create test directory
    pxt.create_dir('asi_arch_test')
    
    # Create experiments table
    experiments = pxt.create_table(
        'asi_arch_test.experiments',
        {
            'experiment_id': pxt.String,
            'generation': pxt.Int,
            'target_capability': pxt.String,
            'status': pxt.String,
            'research_prompt': pxt.String,  # Input for AI research
        }
    )
    
    print("✅ Experiments table created")
    
    # Use Pixeltable's built-in Anthropic function for research
    from pixeltable.functions import anthropic
    
    # Create messages for the researcher agent (user message only)
    messages = [
        {'role': 'user', 'content': experiments.research_prompt}
    ]
    
    # Add computed column with Anthropic researcher
    experiments.add_computed_column(
        research_output=anthropic.messages(
            messages=messages,
            model='claude-3-5-sonnet-20241022',
            max_tokens=2000,
            model_kwargs={
                'system': """You are an AI researcher specializing in neural architecture design. 
Generate novel, scientifically-grounded architecture hypotheses.

Respond in valid JSON format with these fields:
{
    "hypothesis": "Clear description of the novel architecture",
    "motivation": "Scientific reasoning and expected benefits", 
    "code_template": "PyTorch implementation skeleton",
    "expected_improvements": "Specific performance predictions",
    "risk_assessment": "Potential failure modes and mitigations",
    "novelty_score": 0.8,
    "confidence": 0.7
}""",
                'temperature': 0.8,
                'top_p': 0.9
            }
        )
    )
    
    # Extract the text response
    experiments.add_computed_column(
        research_text=experiments.research_output.content[0].text
    )
    
    print("✅ Computed columns added")
    
    # Insert test data
    experiments.insert([{
        'experiment_id': 'exp_001',
        'generation': 1,
        'target_capability': 'reasoning',
        'status': 'pending',
        'research_prompt': f'Generate a novel transformer architecture variant for generation 1 targeting improved reasoning capabilities. Consider efficiency and sub-quadratic complexity.'
    }])
    
    print("✅ Test data inserted")
    
    # Query the results
    results = experiments.select(
        experiments.experiment_id,
        experiments.generation,
        experiments.target_capability,
        experiments.research_text
    ).collect()
    
    print("✅ Researcher agent executed successfully!")
    print("\n=== AI-Generated Research Output ===")
    
    df = results.to_pandas()
    research_output = df.iloc[0]['research_text']
    print(research_output)
    
    # Try to parse as JSON
    try:
        parsed = json.loads(research_output)
        print("\n✅ Valid JSON generated!")
        print(f"Hypothesis: {parsed.get('hypothesis', 'N/A')}")
        print(f"Novelty Score: {parsed.get('novelty_score', 'N/A')}")
    except json.JSONDecodeError:
        print("\n⚠️ Output is not valid JSON, but generation worked!")
    
    # Clean up
    pxt.drop_dir('asi_arch_test', force=True)
    print("\n✅ Test completed and cleaned up")
    
    return True

def test_simple_fitness_udf():
    """Test a simple fitness evaluation UDF"""
    
    pxt.init()
    
    # Create a simple fitness UDF
    @pxt.udf
    def simple_fitness(benchmark_scores: dict) -> float:
        """Simple fitness evaluator"""
        if not benchmark_scores:
            return 0.5
        
        scores = list(benchmark_scores.values())
        return sum(scores) / len(scores) if scores else 0.5
    
    print("✅ Fitness UDF created")
    
    # Test the UDF directly
    test_scores = {"accuracy": 0.85, "efficiency": 0.75}
    
    # Create a simple test table
    if 'fitness_test' in pxt.list_dirs():
        pxt.drop_dir('fitness_test', force=True)
    
    pxt.create_dir('fitness_test')
    
    test_table = pxt.create_table(
        'fitness_test.scores',
        {
            'experiment_id': pxt.String,
            'benchmark_scores': pxt.Json
        }
    )
    
    # Add computed column
    test_table.add_computed_column(
        fitness_score=simple_fitness(test_table.benchmark_scores)
    )
    
    # Test data
    test_table.insert([{
        'experiment_id': 'test_001',
        'benchmark_scores': test_scores
    }])
    
    # Query results
    results = test_table.select(
        test_table.experiment_id,
        test_table.benchmark_scores,
        test_table.fitness_score
    ).collect()
    
    print("✅ Fitness UDF test completed!")
    print(results.to_pandas())
    
    # Clean up
    pxt.drop_dir('fitness_test', force=True)

if __name__ == "__main__":
    print("🚀 Testing ASI-ARCH Researcher Agent (Correct Version)")
    
    print("\n=== Test 1: Researcher Agent with Anthropic ===")
    test_researcher_agent()
    
    print("\n=== Test 2: Simple Fitness UDF ===")
    test_simple_fitness_udf()
    
    print("\n🎉 All tests completed successfully!")
    print("Ready to implement the full ASI-ARCH system!")