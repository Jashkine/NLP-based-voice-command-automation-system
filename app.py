"""Flask web application for voice command automation."""

from flask import Flask, render_template, jsonify, request
from src.processor import VoiceCommandProcessor
import json
import logging

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize processor
try:
    processor = VoiceCommandProcessor()
    logger.info("VoiceCommandProcessor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize processor: {e}")
    processor = None


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/process-voice', methods=['POST'])
def process_voice():
    """Process voice input and return JSON command."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'}), 400
        
        if not processor:
            return jsonify({'status': 'error', 'message': 'Processor not initialized'}), 500
        
        # Process the text
        result = processor.process_text(text)
        
        # Log to console
        print("\n" + "="*70)
        print("VOICE COMMAND RECEIVED")
        print("="*70)
        print(f"Input: {text}")
        print("\nJSON Output:")
        print(json.dumps(result, indent=2))
        print("="*70 + "\n")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/status')
def status():
    """Get system status."""
    try:
        if processor:
            status_info = processor.get_status()
            return jsonify(status_info)
        else:
            return jsonify({'status': 'error', 'message': 'Processor not initialized'}), 500
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("VOICE COMMAND AUTOMATION - WEB INTERFACE")
    print("="*70)
    print("Starting Flask server...")
    print("Open browser: http://localhost:5000")
    print("="*70 + "\n")
    app.run(debug=True, port=5000)
