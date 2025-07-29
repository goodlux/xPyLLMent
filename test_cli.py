#!/usr/bin/env python3
"""
Quick test of the ASI-ARCH interactive CLI
"""

import subprocess
import sys

def test_cli_help():
    """Test that CLI help works"""
    result = subprocess.run([
        sys.executable, "-m", "xpyllment.interactive_cli", "--help"
    ], capture_output=True, text=True, cwd="/Users/rob/repos/xPyLLMent")
    
    print("CLI Help Test:")
    print("Return code:", result.returncode)
    print("STDOUT:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:200])
    
    return result.returncode == 0

def test_commands():
    """Test individual command help"""
    commands = ["init", "discover", "results", "list", "status", "snapshot"]
    
    for cmd in commands:
        print(f"\n--- Testing {cmd} --help ---")
        result = subprocess.run([
            sys.executable, "-m", "xpyllment.interactive_cli", cmd, "--help"
        ], capture_output=True, text=True, cwd="/Users/rob/repos/xPyLLMent")
        
        print(f"{cmd} return code:", result.returncode)
        if result.returncode == 0:
            print(f"✅ {cmd} help works")
        else:
            print(f"❌ {cmd} help failed")
            print("STDERR:", result.stderr[:200])

if __name__ == "__main__":
    print("🧠 Testing ASI-ARCH Interactive CLI\n")
    
    if test_cli_help():
        print("✅ Basic CLI help works!")
    else:
        print("❌ Basic CLI help failed!")
        sys.exit(1)
    
    test_commands()
    
    print("\n🎉 CLI tests complete!")
    print("\nTo use the CLI:")
    print("uv run python -m xpyllment.interactive_cli init")
    print("uv run python -m xpyllment.interactive_cli discover")