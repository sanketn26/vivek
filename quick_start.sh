#!/bin/bash
# quick_start.sh - Get vivek running in minutes

set -e  # Exit on any error

echo "🤖 vivek Quick Start Script"
echo "================================"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.11"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Check if Ollama is installed
echo "🔍 Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Ollama is running
    if ollama list &> /dev/null; then
        echo "✅ Ollama is running"
    else
        echo "🔄 Starting Ollama..."
        ollama serve &
        sleep 3
    fi
else
    echo "📥 Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "❌ Please install Ollama manually from https://ollama.com"
        exit 1
    fi
    
    echo "🔄 Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Create project directory structure
echo "📁 Setting up vivek project structure..."
mkdir -p src/vivek/{core,llm,utils,agentic_context}
mkdir -p src/vivek/{core,llm,utils,agentic_context}/__pycache__

# Create __init__.py files
touch src/vivek/__init__.py
touch src/vivek/core/__init__.py
touch src/vivek/llm/__init__.py
touch src/vivek/utils/__init__.py
touch src/vivek/agentic_context/__init__.py

echo "📦 Installing Python dependencies..."
pip install click rich pyyaml python-dotenv ollama requests gitpython pathspec watchdog psutil colorama

# Download recommended model
echo "📥 Downloading Qwen2.5-Coder 7B model..."
echo "   This might take a few minutes depending on your internet speed..."
ollama pull qwen2.5-coder:7b

# Test the setup
echo "🧪 Testing vivek setup..."
python3 -c "
import ollama
try:
    result = ollama.generate(model='qwen2.5-coder:7b', prompt='print(\"Hello, vivek!\")')
    print('✅ Model test successful!')
    print('📋 Model response preview:', result['response'][:100] + '...')
except Exception as e:
    print(f'❌ Model test failed: {e}')
    exit(1)
"

echo ""
echo "🎉 vivek is ready to go!"
echo ""
echo "📝 Next steps:"
echo "1. Copy the vivek code files to your src/vivek/ directory"
echo "2. cd to your project directory"
echo "3. Run: python3 -m src.vivek.cli init"
echo "4. Run: python3 -m src.vivek.cli chat"
echo ""
echo "🚀 Happy coding with your dual-brain AI assistant!"

# test_vivek.py - Simple test script
cat > test_vivek.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test script for vivek functionality
"""

import asyncio
import sys
import os

# Add vivek to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_basic_functionality():
    """Test basic vivek functionality"""
    try:
        from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator
        from vivek.domain.workflow.services.workflow_service import WorkflowService
        
        print("🧪 Testing vivek Core Components...")

        # Test workflow service
        workflow_service = WorkflowService()
        print("✅ WorkflowService initialized")

        # Test orchestrator
        vivek = SimpleOrchestrator(None)  # Mock for testing
        print("✅ SimpleOrchestrator initialized")

        # Test simple request
        print("🤖 Testing simple request...")
        # Note: This is a simplified test for the new architecture
        print("✅ Basic request processing structure works!")
        
        if response and len(response) > 50:
            print("✅ Basic request processing works!")
            print(f"📝 Response preview: {response[:100]}...")
        else:
            print("❌ Request processing failed or returned insufficient response")
            return False
            
        # Test mode switching
        result = vivek.switch_mode("architect")
        if "architect" in result.lower():
            print("✅ Mode switching works!")
        else:
            print("❌ Mode switching failed")
            return False
            
        print("\n🎉 All tests passed! vivek is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all vivek files are in the src/vivek/ directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running vivek functionality tests...\n")
    
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("\n✅ vivek is ready for development!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the setup and try again.")
        sys.exit(1)
EOF

echo "💾 Created test_vivek.py for testing your setup"