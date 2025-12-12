# Voice Command Web Interface

A beautiful web-based interface for the voice command automation system.

## Features

- 🎤 **Command Input**: Enter voice commands as text
- 📊 **JSON Output**: Real-time display of processed commands
- 🎨 **Modern UI**: Responsive design with gradient styling
- 📋 **Copy to Clipboard**: Easy JSON export
- ✨ **Status Indicators**: Visual feedback on command processing

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start the Web Server
```bash
cd /home/lg/Desktop/others/projects/Auto_control
.venv/bin/python app.py
```

### 3. Open in Browser
Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Enter a Command**: Type or paste a voice command in the input field
2. **Click "Process Command"**: The command will be processed and converted to JSON
3. **View Output**: The JSON output will be displayed and printed to the console
4. **Copy JSON**: Click "Copy JSON" to copy the output to your clipboard
5. **Clear**: Click "Clear" to reset and start over

## Example Commands

- "stop tracking"
- "start tracking"
- "arm the system"
- "disarm the system"
- "rotate left"
- "rotate right"
- "increase altitude"
- "decrease altitude"

## Console Output

When a command is processed, the JSON output is also printed to the console where the Flask server is running:

```
======================================================================
VOICE COMMAND RECEIVED
======================================================================
Input: stop tracking
JSON Output:
{
  "status": "success",
  "command": {
    "timestamp": "2025-12-12T10:03:05.838855",
    "command_type": "tracking",
    "intent": "stop_tracking",
    "confidence": 0.78,
    "parameters": {"action": "stop", "immediate": "true"}
  }
}
======================================================================
```

## Architecture

### Backend (Flask)
- `app.py`: Flask application with routes for processing commands
- Routes:
  - `GET /`: Serve the web interface
  - `POST /api/process-voice`: Process text input and return JSON
  - `GET /api/status`: Get system status

### Frontend (HTML/CSS/JS)
- `templates/index.html`: Single-page application with:
  - Modern responsive UI
  - Real-time command processing
  - JSON output display
  - Copy-to-clipboard functionality

## Integration with Voice Command System

The web interface integrates seamlessly with the core voice command system:

1. **Text Input** → VoiceCommandProcessor
2. **NLU Processing** → Intent classification (TF-IDF)
3. **Command Mapping** → JSON generation
4. **Authorization** → Security checks
5. **JSON Output** → Display + Console logging

## Customization

### Change Port
Edit `app.py` and modify the port number:
```python
app.run(debug=True, port=8000)  # Change 5000 to your port
```

### Add More Commands
Edit `config/intents.yaml` and `config/commands.yaml` to add new voice commands.

### Style Customization
Edit the CSS in `templates/index.html` to customize colors, fonts, and layout.

## Troubleshooting

### Port Already in Use
If port 5000 is already in use:
```bash
.venv/bin/python -c "from app import app; app.run(port=8000)"
```

### Processor Not Initializing
Ensure the configuration files exist:
- `config/intents.yaml`
- `config/commands.yaml`

Check logs for detailed error messages.

### Browser Can't Connect
- Ensure Flask server is running
- Check that you're accessing `http://localhost:5000` (not https)
- Verify no firewall is blocking port 5000

## Production Deployment

For production use, replace the development server:

```bash
# Install production WSGI server
uv pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### POST /api/process-voice

**Request:**
```json
{
  "text": "stop tracking the target"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "command": {
    "timestamp": "2025-12-12T10:03:05.838855",
    "command_type": "tracking",
    "intent": "stop_tracking",
    "confidence": 0.78,
    "transcribed_text": "stop tracking the target",
    "parameters": {
      "action": "stop",
      "immediate": "true"
    },
    "description": "Stop tracking the target",
    "status": "authorized"
  },
  "transcribed_text": "stop tracking the target",
  "intent": "stop_tracking",
  "confidence": 0.78
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Error description here"
}
```

### GET /api/status

**Response:**
```json
{
  "status": "ready",
  "intents_loaded": 10,
  "commands_loaded": 10
}
```

## License

MIT - See LICENSE file for details
