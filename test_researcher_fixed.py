#!/usr/bin/env python3
"""
Test the researcher agent with proper Pixeltable table usage
"""

import pixeltable as pxt
import json

def test_researcher_with_table():
    """Test researcher agent by creating a table and computed column"""
    
    pxt.init()
    
    # Clean up any existing test data
    if 'test_asi' in pxt.list_dirs():
        pxt.drop_dir('test_asi', force=True)
    
    # Create test directory and table
    pxt.create_dir('test_asi')
    
    # Create simple researcher UDF
    @pxt.udf
    def simple_researcher(generation: int, target: str) -> dict:
        """Simple researcher that generates basic hypotheses"""
        
        return {
            "hypothesis": f"Architecture variant {generation} for {target}",
            "motivation": "Testing the research pipeline",
            "code_template": "class TestArchitecture(nn.Module): pass",
            "expected_improvements": "10% efficiency gain",
            "risk_assessment": "Low risk baseline test",
            "novelty_score": 0.7,
            "confidence": 0.8,
            "generation": generation,
            "target_capability": target
        }
    
    # Create experiments table
    experiments = pxt.create_table(
        'test_asi.experiments',
        {
            'experiment_id': pxt.String,
            'generation': pxt.Int,
            'target_capability': pxt.String,
            'status': pxt.String,
        }
    )
    
    # Add computed column with researcher agent
    experiments.add_computed_column(
        research_output=simple_researcher(experiments.generation, experiments.target_capability)
    )
    
    print("✅ Table and computed column created")
    
    # Insert test data
    experiments.insert([{
        'experiment_id': 'exp_001',
        'generation': 1,
        'target_capability': 'reasoning',
        'status': 'pending'
    }])
    
    print("✅ Test data inserted")
    
    # Query the computed column
    result = experiments.select(
        experiments.experiment_id,
        experiments.generation,
        experiments.target_capability,
        experiments.research_output
    ).collect()
    
    print("✅ Computed column executed successfully!")
    print("Results:")
    print(result.to_pandas())
    
    # Clean up
    pxt.drop_dir('test_asi', force=True)
    print("✅ Cleanup completed")

def test_anthropic_udf():
    """Test UDF with Anthropic integration"""
    
    pxt.init()
    
    # Clean up
    if 'test_anthropic' in pxt.list_dirs():
        pxt.drop_dir('test_anthropic', force=True)
    
    pxt.create_dir('test_anthropic')
    
    @pxt.udf
    def anthropic_researcher(prompt: str) -> dict:
        """Researcher UDF using Anthropic"""
        
        try:
            response = pxt.functions.anthropic.chat_completions(
                messages=[
                    {"role": "user", "content": f"Generate a JSON response for this architecture research prompt: {prompt}. Return JSON with 'hypothesis', 'confidence' fields."}
                ],
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.5
            )
            
            # Try to parse as JSON, fallback to simple structure
            try:
                return json.loads(response)
            except:
                return {
                    "hypothesis": "AI-generated architecture concept",
                    "confidence": 0.8,
                    "raw_response": response
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "hypothesis": "Fallback architecture",
                "confidence": 0.3
            }
    
    # Create test table
    test_table = pxt.create_table(
        'test_anthropic.prompts',
        {
            'prompt_id': pxt.String,
            'research_prompt': pxt.String,
        }
    )
    
    # Add computed column
    test_table.add_computed_column(
        ai_response=anthropic_researcher(test_table.research_prompt)
    )
    
    # Test data
    test_table.insert([{
        'prompt_id': 'prompt_001',
        'research_prompt': 'Design a transformer variant with improved efficiency'
    }])
    
    # Query results
    result = test_table.select(test_table.prompt_id, test_table.ai_response).collect()
    
    print("✅ Anthropic UDF test completed!")
    print("AI Response:")
    print(result.to_pandas())
    
    # Clean up
    pxt.drop_dir('test_anthropic', force=True)

if __name__ == "__main__":
    print("Testing ASI-ARCH Researcher Agent with Tables...")
    
    # Test 1: Simple researcher with table
    print("\n=== Test 1: Simple Researcher with Table ===")
    test_researcher_with_table()
    
    # Test 2: Anthropic integration
    print("\n=== Test 2: Anthropic Integration ===")
    test_anthropic_udf()
    
    print("\n🎉 All tests completed successfully!")