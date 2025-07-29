#!/usr/bin/env python3
"""
Test downloading a few papers
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_small_download():
    print("🧪 Testing small ArXiv paper download...")
    
    try:
        from xpyllment.arxiv_ingestion import ArXivIngestionSystem
        
        # Create system with test directory
        test_dir = Path.home() / '.pixeltable' / 'test_papers'
        system = ArXivIngestionSystem(data_dir=test_dir)
        
        print("✅ ArXiv system created")
        
        # Search for just 3 papers
        papers = system.search_papers(
            categories=["cs.AI"],
            max_results=3, 
            date_range="1w"  # Last week only
        )
        
        print(f"✅ Found {len(papers)} papers")
        
        if papers:
            # Try to download just the first one
            print(f"\n📥 Attempting to download first paper: {papers[0]['title'][:50]}...")
            
            downloaded = system.download_papers([papers[0]])
            
            if downloaded and downloaded[0].get('processing_status') == 'downloaded':
                print("✅ Download successful!")
                
                # Check file exists
                pdf_path = Path(downloaded[0]['pdf_path'])
                if pdf_path.exists():
                    print(f"✅ File exists: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")
                    
                    # Clean up test file
                    pdf_path.unlink()
                    print("🧹 Cleaned up test file")
                else:
                    print("❌ File was not created")
            else:
                print("❌ Download failed")
        
        print("\n🎉 Download test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_small_download()