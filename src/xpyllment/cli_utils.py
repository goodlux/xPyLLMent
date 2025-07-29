"""
CLI utilities for handling different terminal environments
"""

import sys
import os
from typing import Any, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

def is_interactive_terminal() -> bool:
    """Check if we're in a real interactive terminal"""
    return (
        sys.stdin.isatty() and 
        sys.stdout.isatty() and 
        os.environ.get('TERM') != 'dumb'
    )

def safe_confirm(message: str, default: bool = False) -> bool:
    """Safe confirmation prompt with fallback"""
    if not is_interactive_terminal():
        console.print(f"⚠️  Non-TTY environment: Using default ({default}) for: {message}")
        return default
    
    try:
        return Confirm.ask(message, default=default)
    except (EOFError, KeyboardInterrupt):
        console.print(f"⚠️  Input error: Using default ({default})")
        return default

def safe_prompt(message: str, choices: List[str], default: str) -> str:
    """Safe prompt with fallback"""
    if not is_interactive_terminal():
        console.print(f"⚠️  Non-TTY environment: Using default ({default}) for: {message}")
        return default
    
    try:
        return Prompt.ask(message, choices=choices, default=default)
    except (EOFError, KeyboardInterrupt):
        console.print(f"⚠️  Input error: Using default ({default})")
        return default

def safe_int_prompt(message: str, default: int) -> int:
    """Safe integer prompt with fallback"""
    if not is_interactive_terminal():
        console.print(f"⚠️  Non-TTY environment: Using default ({default}) for: {message}")
        return default
    
    try:
        from rich.prompt import IntPrompt
        return IntPrompt.ask(message, default=default)
    except (EOFError, KeyboardInterrupt):
        console.print(f"⚠️  Input error: Using default ({default})")
        return default

def detect_environment() -> dict:
    """Detect and report the current environment"""
    return {
        'is_tty': sys.stdin.isatty(),
        'is_interactive': is_interactive_terminal(),
        'term': os.environ.get('TERM', 'unknown'),
        'shell': os.environ.get('SHELL', 'unknown'),
        'platform': sys.platform,
        'python_version': sys.version.split()[0]
    }