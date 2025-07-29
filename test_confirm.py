#!/usr/bin/env python3
"""
Test the Rich Confirm prompt to see if it hangs
"""

from rich.console import Console
from rich.prompt import Confirm

console = Console()

print("Testing Rich Confirm prompt...")
console.print("🔄 About to ask for confirmation...")

try:
    result = Confirm.ask("🔄 Reset existing database?", default=False)
    console.print(f"✅ Got result: {result}")
except KeyboardInterrupt:
    console.print("❌ Interrupted by user")
except Exception as e:
    console.print(f"❌ Error: {e}")

print("Test complete!")