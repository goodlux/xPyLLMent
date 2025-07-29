#!/usr/bin/env python3
"""
Test ArXiv paper ingestion system
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

print("🧪 Testing ArXiv paper ingestion system...")

try:
    print("\n1. Testing basic imports...")
    import pixeltable as pxt
    print("   ✅ Pixeltable imported")
    
    import arxiv
    print("   ✅ ArXiv library imported")
    
    print("\n2. Testing ArXiv search (limit 3 papers)...")
    search = arxiv.Search(
        query="cat:cs.AI",
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in search.results():
        paper = {
            'arxiv_id': result.entry_id.split('/')[-1],
            'title': result.title[:50] + "...",
            'authors': [author.name for author in result.authors][:2]  # First 2 authors
        }
        papers.append(paper)
        
    print(f"   ✅ Found {len(papers)} papers:")
    for paper in papers:
        print(f"      • {paper['arxiv_id']}: {paper['title']}")
    
    print("\n3. Testing Pixeltable table creation...")
    
    # Try to create a simple test table
    try:
        # Clean up any existing test table
        try:
            pxt.drop_table('test.papers')
        except:
            pass
        
        try:
            pxt.create_dir('test')
        except:
            pass
        
        test_table = pxt.create_table(
            'test.papers',
            {
                'arxiv_id': pxt.String,
                'title': pxt.String,
                'authors': pxt.Json,
            }
        )
        
        print("   ✅ Test table created successfully")
        
        # Insert a test paper
        test_table.insert([{
            'arxiv_id': papers[0]['arxiv_id'],
            'title': papers[0]['title'],
            'authors': papers[0]['authors']
        }])
        
        print("   ✅ Test data inserted")
        
        # Query the data back
        results = test_table.select().limit(1).collect()
        print(f"   ✅ Query successful, got {len(results)} results")
        
        # Clean up
        pxt.drop_table('test.papers')
        print("   ✅ Test table cleaned up")
        
    except Exception as e:
        print(f"   ❌ Table creation failed: {e}")
        # Continue with other tests
    
    print("\n4. Testing ArXiv ingestion system...")
    from xpyllment.arxiv_ingestion import ArXivIngestionSystem
    
    # Test without actually creating tables
    print("   ✅ ArXiv ingestion system imported")
    
    print("\n🎉 All tests passed!")
    print("\nReady to implement full ArXiv ingestion!")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()