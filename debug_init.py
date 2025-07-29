#!/usr/bin/env python3
"""
Debug ASI-ARCH initialization issues
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

print("🔍 Debugging ASI-ARCH initialization...")

try:
    print("1. Testing basic imports...")
    import pixeltable as pxt
    print("   ✅ Pixeltable imported successfully")
    
    print("2. Testing Pixeltable initialization...")
    # Test if Pixeltable needs initialization
    try:
        tables = pxt.list_tables()
        print(f"   ✅ Pixeltable is initialized, found {len(tables)} tables")
    except Exception as e:
        print(f"   ⚠️  Pixeltable not initialized: {e}")
        print("   🔧 Trying to initialize Pixeltable...")
        try:
            pxt.init()
            print("   ✅ Pixeltable initialized successfully")
            tables = pxt.list_tables()
            print(f"   ✅ Found {len(tables)} tables after init")
        except Exception as init_e:
            print(f"   ❌ Pixeltable initialization failed: {init_e}")
    
    print("3. Testing directory listing...")
    try:
        dirs = pxt.list_dirs()
        print(f"   ✅ Found {len(dirs)} directories")
    except Exception as e:
        print(f"   ⚠️  Directory listing failed: {e}")
    
    print("4. Testing ASI-ARCH imports...")
    from xpyllment.asi_arch import ASIArch
    print("   ✅ ASI-ARCH imported successfully")
    
    print("5. Testing ASI-ARCH initialization (this is where it might hang)...")
    print("   🔄 Creating ASI-ARCH instance...")
    
    # Try with a timeout
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("ASI-ARCH initialization timed out")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    try:
        system = ASIArch(reset_db=False)
        signal.alarm(0)  # Cancel timeout
        print("   ✅ ASI-ARCH created successfully!")
        
        print("6. Testing system status...")
        experiments = system.list_experiments(limit=1)
        print(f"   ✅ System working, found {len(experiments)} experiments")
        
    except TimeoutError:
        signal.alarm(0)
        print("   ❌ ASI-ARCH initialization timed out after 10 seconds")
        print("   💡 This suggests a database connection or table creation issue")
    except Exception as e:
        signal.alarm(0)
        print(f"   ❌ ASI-ARCH initialization failed: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"❌ Debug failed at step: {e}")
    traceback.print_exc()

print("\n🔍 Debug complete!")