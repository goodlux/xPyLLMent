#!/usr/bin/env python3
"""
Test the CLI input handling
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_input_mapping():
    """Test the input mapping logic"""
    
    print("🧪 Testing CLI input mapping...")
    
    # Test paper choice mapping
    option_map = {
        "1": "arxiv", 
        "2": "local",
        "3": "demo", 
        "4": "skip"
    }
    
    test_inputs = ["1", "2", "3", "4", "arxiv", "demo", "invalid", ""]
    
    print("\n📚 Paper choice mapping:")
    for user_input in test_inputs:
        paper_choice = option_map.get(user_input, user_input)
        
        # Validate the choice
        valid_choices = ["arxiv", "local", "demo", "skip"]
        if paper_choice not in valid_choices:
            print(f"  '{user_input}' -> INVALID -> fallback to 'demo'")
        else:
            print(f"  '{user_input}' -> '{paper_choice}' ✅")
    
    # Test model choice mapping
    model_option_map = {
        "1": "ollama",
        "2": "huggingface", 
        "3": "anthropic",
        "4": "custom",
        "5": "skip"
    }
    
    test_model_inputs = ["1", "2", "3", "4", "5", "anthropic", "ollama", "bad_input"]
    
    print("\n🤖 Model choice mapping:")
    for user_input in test_model_inputs:
        model_choice = model_option_map.get(user_input, user_input)
        
        # Validate the choice
        valid_model_choices = ["ollama", "huggingface", "anthropic", "custom", "skip"]
        if model_choice not in valid_model_choices:
            print(f"  '{user_input}' -> INVALID -> fallback to 'anthropic'")
        else:
            print(f"  '{user_input}' -> '{model_choice}' ✅")
    
    print("\n🎉 Input mapping test complete!")

if __name__ == "__main__":
    test_input_mapping()