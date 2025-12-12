#!/bin/bash
# Getting Started Script - One-command setup and test

set -e

echo "🚀 Voice Command Automation System - Getting Started"
echo "=================================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv is ready"
echo ""

# Install dependencies
echo "📚 Installing dependencies (this may take 2-5 minutes)..."
uv sync
echo "✅ Dependencies installed"
echo ""

# Initialize configuration
echo "⚙️  Initializing configuration files..."
uv run python -c "from src.cli import init_config; import click; 
ctx = click.Context(click.Command('init'))
ctx.obj = {'debug': False}
init_config.callback(None, None)"

echo "✅ Configuration initialized"
echo ""

# Run first test
echo "🧪 Running first test..."
echo ""
echo "Input: 'stop tracking'"
echo ""

result=$(uv run python -c "
from src.processor import VoiceCommandProcessor
import json
processor = VoiceCommandProcessor(use_mock=True)
result = processor.process_text('stop tracking')
if result['status'] == 'success':
    print(json.dumps(result['command'], indent=2))
else:
    print('Error:', result.get('error', 'Unknown error'))
")

echo "Output:"
echo "$result"
echo ""

# Test audio processing (if available)
echo "📝 System Status:"
uv run python -c "
from src.processor import VoiceCommandProcessor
processor = VoiceCommandProcessor(use_mock=True)
status = processor.get_status()
print(f'  • Intents loaded: {status[\"intents_loaded\"]}')
print(f'  • Commands loaded: {status[\"commands_loaded\"]}')
print(f'  • ASR Model: {status[\"asr_model\"]}')
print(f'  • NLU Model: {status[\"nlu_model\"]}')
"
echo ""

echo "=================================================="
echo "✨ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Try processing text:"
echo "   voice-control process-text 'stop tracking' --pretty"
echo ""
echo "2. Process an audio file:"
echo "   voice-control process-audio audio.wav --pretty"
echo ""
echo "3. Check system status:"
echo "   voice-control status"
echo ""
echo "4. Learn more:"
echo "   • Read: QUICKSTART.md (5 minute guide)"
echo "   • Read: README.md (complete documentation)"
echo "   • Review: examples.py (code examples)"
echo ""
echo "5. Customize:"
echo "   • Edit config/intents.yaml (add voice patterns)"
echo "   • Edit config/commands.yaml (add commands)"
echo ""
echo "Ready to go! 🚀"
