# Quick Reference Guide

## Installation (5 minutes)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone/navigate to project
cd /home/lg/Desktop/others/projects/Auto_control

# Install dependencies
uv sync
```

## Essential Commands

### Initialize Configuration
```bash
voice-control init-config
```

### Process Audio File
```bash
voice-control process-audio audio.wav --pretty --output command.json
```

### Process Text Command
```bash
voice-control process-text "stop tracking" --pretty
```

### Check System Status
```bash
voice-control status
```

## Configuration Files

### Intents (config/intents.yaml)
```yaml
command_name:
  patterns:
    - "user says this"
    - "or this variation"
  actions:
    description: "What it does"
```

### Commands (config/commands.yaml)
```yaml
command_name:
  command_type: "control"
  parameters:
    action: "stop"
  description: "Command description"
```

## Python Usage

```python
from src.processor import VoiceCommandProcessor

# Initialize
processor = VoiceCommandProcessor()

# Process text
result = processor.process_text("stop tracking")
if result["status"] == "success":
    print(result["command"])

# Process audio
result = processor.process_audio("audio.wav")
```

## Output JSON Format

```json
{
  "timestamp": "2024-12-12T10:30:45.123456",
  "command_type": "tracking",
  "intent": "stop_tracking",
  "confidence": 0.95,
  "transcribed_text": "Can you stop tracking?",
  "parameters": {
    "action": "stop",
    "immediate": "true"
  },
  "description": "Stop tracking the target",
  "status": "authorized"
}
```

## Environment Variables

```bash
# Set model sizes
export ASR__MODEL_NAME=base           # tiny, base, small, medium, large
export NLU__CONFIDENCE_THRESHOLD=0.7  # 0.0 to 1.0

# Set device
export ASR__DEVICE=cpu                # cpu or cuda
export NLU__DEVICE=cpu

# Debug mode
export DEBUG=true
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| CUDA out of memory | Set `ASR__DEVICE=cpu` |
| Slow inference | Use smaller models: `ASR__MODEL_NAME=tiny` |
| Low accuracy | Lower threshold: `NLU__CONFIDENCE_THRESHOLD=0.6` |
| File not found | Use absolute paths |

## Pre-configured Commands

- `stop tracking` - Stop tracking target
- `start tracking` - Start tracking target
- `reset system` - Reset to defaults
- `emergency stop` - Immediate shutdown
- `increase speed` - Speed up system
- `decrease speed` - Slow down
- `get status` - Request status
- `lock target` - Lock current target
- `release target` - Release target

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_processor.py -v

# With coverage
uv run pytest --cov=src
```

## File Structure Quick Reference

```
Auto_control/
├── src/                   # Main code
│   ├── asr.py            # Speech recognition
│   ├── nlu.py            # Intent classification
│   ├── mapper.py         # Command generation
│   ├── processor.py      # Main orchestrator
│   └── cli.py            # Command line
├── config/               # Configuration files
│   ├── intents.yaml      # Intent definitions
│   └── commands.yaml     # Command mappings
├── tests/                # Test files
├── pyproject.toml        # Project config (uv)
└── README.md             # Full documentation
```

## Common Tasks

### Add New Voice Command

1. Edit `config/intents.yaml`:
```yaml
my_command:
  patterns:
    - "say this"
  actions:
    description: "Does this"
```

2. Edit `config/commands.yaml`:
```yaml
my_command:
  command_type: "my_type"
  parameters:
    action: "my_action"
  description: "Description"
```

3. Test:
```bash
voice-control process-text "say this" --pretty
```

### Change Model Size

Edit `.env`:
```bash
# Smaller (faster, less memory)
ASR__MODEL_NAME=tiny

# Default (balanced)
ASR__MODEL_NAME=base

# Larger (slower, more accurate)
ASR__MODEL_NAME=small
```

### Use GPU

```bash
# In .env
ASR__DEVICE=cuda
NLU__DEVICE=cuda
```

### Increase Authorization Threshold

```bash
# In .env
NLU__CONFIDENCE_THRESHOLD=0.85
```

## Support

- Full docs: See `README.md`
- Architecture: See `ARCHITECTURE.md`
- Examples: See examples/ directory
- Tests: See tests/ directory
