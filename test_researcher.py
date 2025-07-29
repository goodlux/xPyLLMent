#!/usr/bin/env python3
"""
Test the researcher agent UDF creation and basic functionality
"""

import pixeltable as pxt
import json

def test_simple_udf():
    """Test creating a simple UDF first"""
    
    pxt.init()
    
    # Create a simple test UDF
    @pxt.udf
    def simple_test_udf(text: str) -> str:
        return f"Processed: {text}"
    
    print("✅ Simple UDF created successfully")
    
    # Test the UDF
    result = simple_test_udf("Hello ASI-ARCH!")
    print(f"UDF result: {result}")
    
    return simple_test_udf

def test_researcher_agent_simple():
    """Test researcher agent with minimal functionality"""
    
    pxt.init()
    
    # Create simplified researcher agent
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
    
    print("✅ Simple researcher agent created")
    
    # Test the researcher
    result = simple_researcher(1, "reasoning")
    print(f"Research result: {json.dumps(result, indent=2)}")
    
    return simple_researcher

def test_with_anthropic():
    """Test using Pixeltable's Anthropic integration"""
    
    pxt.init()
    
    try:
        # Test basic Anthropic call
        response = pxt.functions.anthropic.chat_completions(
            messages=[
                {"role": "user", "content": "Generate a simple JSON with a 'test' field containing 'success'"}
            ],
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            temperature=0.1
        )
        
        print("✅ Anthropic integration working")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Anthropic integration failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ASI-ARCH Researcher Agent...")
    
    # Test 1: Simple UDF
    print("\n=== Test 1: Simple UDF ===")
    simple_udf = test_simple_udf()
    
    # Test 2: Simple researcher
    print("\n=== Test 2: Simple Researcher ===")
    researcher = test_researcher_agent_simple()
    
    # Test 3: Anthropic integration
    print("\n=== Test 3: Anthropic Integration ===")
    anthropic_works = test_with_anthropic()
    
    print("\n🎉 All tests completed!")
    print(f"Anthropic working: {anthropic_works}")