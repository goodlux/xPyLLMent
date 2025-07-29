#!/usr/bin/env python3
"""
Test Pixeltable GLiNER Integration

Simple test to verify our GLiNER functions work in Pixeltable
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_pixeltable_gliner():
    """Test our Pixeltable GLiNER integration"""
    
    try:
        import pixeltable as pxt
        from pixeltable.functions.huggingface import gliner_entity_extraction, gliner_research_entities
        
        print("✅ Successfully imported GLiNER from Pixeltable!")
        
        # Initialize Pixeltable
        pxt.init()
        
        # Create test table
        if 'test_gliner' in pxt.list_dirs():
            pxt.drop_dir('test_gliner', force=True)
        
        pxt.create_dir('test_gliner')
        
        # Create simple table for testing
        test_table = pxt.create_table(
            'test_gliner.papers',
            {
                'id': pxt.String,
                'text': pxt.String
            }
        )
        
        print("✅ Created test table")
        
        # Add GLiNER computed column using our official function
        test_table.add_computed_column(
            entities=gliner_research_entities(
                test_table.text,
                threshold=0.5
            )
        )
        
        print("✅ Added GLiNER computed column")
        
        # Insert test data
        test_table.insert([{
            'id': 'test1',
            'text': 'We propose a new transformer architecture for neural machine translation using attention mechanisms and achieving state-of-the-art BLEU scores on the WMT dataset.'
        }])
        
        print("✅ Inserted test data - GLiNER processing will happen automatically!")
        
        # Query results (this triggers GLiNER execution)
        print("🛸 Running GLiNER entity extraction...")
        results = test_table.select(test_table.id, test_table.entities).collect()
        
        df = results.to_pandas()
        if not df.empty:
            entities_data = df.iloc[0]['entities']
            if entities_data and 'entities' in entities_data:
                entities = entities_data['entities']
                print(f"✅ GLiNER extracted {len(entities)} entities!")
                
                print("\n🎯 Extracted entities:")
                for entity in entities[:5]:  # Show first 5
                    print(f"  • {entity['text']} ({entity['label']}) - confidence: {entity['confidence']:.3f}")
            else:
                print("⚠️  No entities extracted")
        
        # Clean up
        pxt.drop_dir('test_gliner', force=True)
        print("\n🎉 GLiNER integration test successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pixeltable_gliner()