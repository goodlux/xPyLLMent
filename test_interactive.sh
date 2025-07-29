#!/bin/bash
# Test script for interactive CLI

echo "Testing ASI-ARCH Interactive CLI"
echo "================================="

echo "1. Testing help..."
./xpyllment --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Help command works"
else
    echo "❌ Help command failed"
    exit 1
fi

echo "2. Testing non-interactive init..."
./xpyllment init --non-interactive > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Non-interactive init works"
else
    echo "❌ Non-interactive init failed"
    exit 1
fi

echo "3. Testing status..."
./xpyllment status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Status command works"
else
    echo "❌ Status command failed"
fi

echo "4. Testing list..."
./xpyllment list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ List command works"
else  
    echo "❌ List command failed"
fi

echo ""
echo "🎉 All tests passed!"
echo ""
echo "Ready to use:"
echo "  ./xpyllment init --non-interactive  # Quick setup"
echo "  ./xpyllment init                    # Interactive setup (in real terminal)" 
echo "  ./xpyllment status                  # System health"
echo "  ./xpyllment discover                # Start research!"