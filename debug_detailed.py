#!/usr/bin/env python3
"""
Detailed debugging of ASI-ARCH initialization process
"""

import sys
import time
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def timeout_handler():
    """Handle timeout by printing stack trace"""
    import traceback
    import os
    print("\n" + "="*60)
    print("⏰ TIMEOUT OCCURRED - Current stack trace:")
    print("="*60)
    traceback.print_stack()
    print("="*60)
    os._exit(1)

print("🔍 Detailed ASI-ARCH initialization debugging...")
print("This will help us find exactly where it hangs\n")

try:
    print("Step 1: Testing basic imports...")
    import pixeltable as pxt
    print("   ✅ Pixeltable imported")
    
    print("Step 2: Testing Pixeltable status...")
    tables = pxt.list_tables()
    print(f"   ✅ Found {len(tables)} existing tables")
    
    print("Step 3: Testing ASI-ARCH import...")
    from xpyllment.asi_arch import ASIArch
    print("   ✅ ASI-ARCH imported")
    
    print("Step 4: Testing ASI-ARCH initialization with timeout...")
    print("   🔄 Creating ASI-ARCH instance (max 30 seconds)...")
    
    # Set up timeout
    timer = threading.Timer(30.0, timeout_handler)
    timer.start()
    
    start_time = time.time()
    
    try:
        # This is the exact line that might be hanging
        system = ASIArch(reset_db=False)
        elapsed = time.time() - start_time
        timer.cancel()
        
        print(f"   ✅ ASI-ARCH created successfully in {elapsed:.2f} seconds!")
        
        print("Step 5: Testing system operations...")
        experiments = system.list_experiments(limit=1)
        print(f"   ✅ Found {len(experiments)} experiments")
        
        print("Step 6: Testing Rich console...")
        from rich.console import Console
        console = Console()
        console.print("   ✅ Rich console working")
        
        print("Step 7: Testing Rich Progress (this might hang)...")
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Testing progress bar...", total=None)
            time.sleep(0.5)  # Brief test
            progress.update(task, description="✅ Progress bar works!")
        
        print("   ✅ Rich Progress working")
        
        print("Step 8: Testing Rich Prompt (this is likely the culprit)...")
        from rich.prompt import Confirm
        
        # Test with timeout
        prompt_timer = threading.Timer(5.0, lambda: print("⏰ Prompt timed out after 5 seconds"))
        prompt_timer.start()
        
        try:
            # This is probably where it hangs
            result = Confirm.ask("Test prompt - answer y or n", default=False)
            prompt_timer.cancel()
            print(f"   ✅ Rich Prompt working, got: {result}")
        except Exception as e:
            prompt_timer.cancel()
            print(f"   ❌ Rich Prompt failed: {e}")
            print("   🎯 FOUND THE ISSUE: Rich prompts don't work in this environment!")
        
    except Exception as e:
        timer.cancel()
        print(f"   ❌ ASI-ARCH initialization failed: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Debug failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Debug complete!")
print("\nIf the script hung, check the timeout stack trace above to see exactly where.")