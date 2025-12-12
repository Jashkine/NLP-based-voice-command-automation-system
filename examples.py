"""Example usage scripts for voice command automation system."""

# Example 1: Basic Text Processing
def example_basic_text():
    """Process a simple text command."""
    from src.processor import VoiceCommandProcessor
    import json
    
    processor = VoiceCommandProcessor()
    result = processor.process_text("stop tracking")
    
    if result["status"] == "success":
        print(json.dumps(result["command"], indent=2))
    else:
        print(f"Error: {result['error']}")


# Example 2: Audio File Processing
def example_audio_file():
    """Process an audio file."""
    from src.processor import VoiceCommandProcessor
    import json
    from pathlib import Path
    
    processor = VoiceCommandProcessor()
    audio_path = Path("voice_command.wav")
    
    result = processor.process_audio(audio_path)
    
    if result["status"] == "success":
        command = result["command"]
        print(f"Recognized: {result['transcribed_text']}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(json.dumps(command, indent=2))


# Example 3: Custom Configuration
def example_custom_config():
    """Use custom configuration."""
    from src.processor import VoiceCommandProcessor
    from src.config import SystemConfig, ASRConfig, NLUConfig
    
    config = SystemConfig(
        asr=ASRConfig(
            model_name="tiny",  # Lightweight model
            device="cpu"
        ),
        nlu=NLUConfig(
            confidence_threshold=0.8  # High confidence required
        )
    )
    
    processor = VoiceCommandProcessor(config)
    result = processor.process_text("increase speed")
    
    print(f"Result: {result['status']}")


# Example 4: Authorization Management
def example_authorization():
    """Manage authorization for commands."""
    from src.mapper import CommandAuthorizationManager
    
    auth = CommandAuthorizationManager(
        authorized_intents=["stop_tracking", "start_tracking"]
    )
    
    # Check if command is authorized
    if auth.is_authorized("stop_tracking", confidence=0.95):
        print("Command is authorized")
    else:
        print("Command is NOT authorized")
    
    # Add new authorized intent
    auth.add_authorized_intent("emergency_stop")
    
    # List all authorized
    print(f"Authorized intents: {auth.list_authorized_intents()}")


# Example 5: JSON Command Generation
def example_json_generation():
    """Generate JSON commands with custom parameters."""
    from src.mapper import CommandMapper
    from src.config import CommandMapping
    import json
    
    commands = {
        "custom_action": CommandMapping(
            intent="custom_action",
            command_type="custom",
            parameters={
                "mode": "manual",
                "priority": "high"
            },
            description="Custom action command"
        )
    }
    
    mapper = CommandMapper(commands)
    
    command = mapper.map_intent_to_command(
        intent="custom_action",
        confidence=0.92,
        transcribed_text="execute custom action"
    )
    
    print(json.dumps(command, indent=2))


# Example 6: Full Pipeline with Error Handling
def example_error_handling():
    """Comprehensive error handling example."""
    from src.processor import VoiceCommandProcessor
    import json
    
    processor = VoiceCommandProcessor()
    
    test_inputs = [
        "stop tracking",
        "unknown random command",
        "start tracking",
        ""
    ]
    
    for text in test_inputs:
        print(f"\nProcessing: '{text}'")
        result = processor.process_text(text, min_confidence=0.7)
        
        print(f"Status: {result['status']}")
        
        if result["status"] == "success":
            print(f"Intent: {result['intent']}")
            print(f"Command: {result['command']['command_type']}")
        elif result["status"] == "rejected":
            print(f"Reason: {result.get('reason', 'Unknown')}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


# Example 7: Configuration Reloading
def example_reload_config():
    """Dynamically reload configurations."""
    from src.processor import VoiceCommandProcessor
    
    processor = VoiceCommandProcessor()
    
    print(f"Initial intents: {processor.get_status()['intents_loaded']}")
    
    # Modify config files (config/intents.yaml, config/commands.yaml)
    
    # Reload
    processor.reload_configurations()
    
    print(f"Updated intents: {processor.get_status()['intents_loaded']}")


# Example 8: Batch Processing
def example_batch_processing():
    """Process multiple commands in batch."""
    from src.processor import VoiceCommandProcessor
    import json
    from pathlib import Path
    
    processor = VoiceCommandProcessor()
    
    commands = [
        "stop tracking",
        "reset system",
        "get status",
        "increase speed"
    ]
    
    results = []
    
    for cmd_text in commands:
        result = processor.process_text(cmd_text)
        if result["status"] == "success":
            results.append({
                "input": cmd_text,
                "intent": result["intent"],
                "command": result["command"]
            })
    
    # Save batch results
    output_file = Path("batch_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} commands")


# Example 9: Integration with External System
def example_external_integration():
    """Example of sending commands to external system."""
    from src.processor import VoiceCommandProcessor
    import json
    import socket
    
    processor = VoiceCommandProcessor()
    result = processor.process_text("stop tracking")
    
    if result["status"] == "success":
        command = result["command"]
        
        # Send to external system via socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 5000))
            sock.send(json.dumps(command).encode())
            sock.close()
            print("Command sent to external system")
        except ConnectionRefusedError:
            print("External system not available")


# Example 10: Status Monitoring
def example_status_monitoring():
    """Monitor system status."""
    from src.processor import VoiceCommandProcessor
    import json
    
    processor = VoiceCommandProcessor()
    
    status = processor.get_status()
    
    print("System Status:")
    print(f"  Intents loaded: {status['intents_loaded']}")
    print(f"  Commands loaded: {status['commands_loaded']}")
    print(f"  ASR Model: {status['asr_model']}")
    print(f"  NLU Model: {status['nlu_model']}")
    print(f"  Authorized intents: {len(status['authorized_intents'])}")
    
    for intent in status['authorized_intents'][:5]:
        print(f"    - {intent}")


if __name__ == "__main__":
    print("Voice Command Automation Examples\n")
    
    print("=" * 50)
    print("Example 1: Basic Text Processing")
    print("=" * 50)
    try:
        example_basic_text()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example 3: Custom Configuration")
    print("=" * 50)
    try:
        example_custom_config()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example 4: Authorization Management")
    print("=" * 50)
    try:
        example_authorization()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example 6: Full Pipeline with Error Handling")
    print("=" * 50)
    try:
        example_error_handling()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Example 10: Status Monitoring")
    print("=" * 50)
    try:
        example_status_monitoring()
    except Exception as e:
        print(f"Error: {e}")
