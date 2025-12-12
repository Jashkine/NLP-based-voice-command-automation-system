"""Command-line interface for voice command automation system."""

import json
from pathlib import Path
from typing import Optional
import click
from loguru import logger
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SystemConfig, get_system_config
from src.processor import VoiceCommandProcessor


def setup_logging(debug: bool = False):
    """Setup logging configuration."""
    log_level = "DEBUG" if debug else "INFO"
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | {name}:{function}:{line} - {message}",
        level=log_level
    )
    logger.add(
        "voice_automation.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="500 MB"
    )


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, debug):
    """Voice Command Automation System for Air-borne Console."""
    setup_logging(debug)
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("--language", default="en", help="Language code (default: en)")
@click.option("--confidence", type=float, default=0.7, help="Minimum confidence threshold")
@click.option("--output", type=click.Path(), help="Save command JSON to file")
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.pass_context
def process_audio(ctx, audio_file, language, confidence, output, pretty):
    """Process audio file and generate command."""
    logger.info(f"Processing audio file: {audio_file}")
    
    try:
        processor = VoiceCommandProcessor(use_mock=ctx.obj.get("debug", False))
        result = processor.process_audio(audio_file, language, confidence)
        
        # Display result
        click.echo("\n" + "="*60)
        click.echo("VOICE COMMAND PROCESSING RESULT")
        click.echo("="*60)
        
        if result["status"] == "success":
            click.secho("✓ Command Generated Successfully", fg="green", bold=True)
            click.echo(f"\nTranscribed Text: {result['transcribed_text']}")
            click.echo(f"Detected Intent: {result['intent']}")
            click.echo(f"Confidence: {result['confidence']:.2%}")
            click.echo("\nGenerated Command:")
            command_json = result["command"]
            click.echo(json.dumps(command_json, indent=2) if pretty else json.dumps(command_json))
            
            # Save to file if requested
            if output:
                with open(output, "w") as f:
                    json.dump(command_json, f, indent=2)
                click.secho(f"\n✓ Command saved to: {output}", fg="green")
        else:
            click.secho(f"✗ Error: {result['status']}", fg="red", bold=True)
            click.echo(f"Error: {result.get('error', 'Unknown error')}")
            if "transcribed_text" in result:
                click.echo(f"Transcribed: {result['transcribed_text']}")
        
        click.echo("="*60)
        
    except Exception as e:
        click.secho(f"✗ Failed to process audio: {e}", fg="red", bold=True)
        logger.exception("Audio processing failed")
        sys.exit(1)


@cli.command()
@click.argument("text")
@click.option("--confidence", type=float, default=0.7, help="Minimum confidence threshold")
@click.option("--output", type=click.Path(), help="Save command JSON to file")
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.pass_context
def process_text(ctx, text, confidence, output, pretty):
    """Process text command and generate JSON."""
    logger.info(f"Processing text: {text}")
    
    try:
        processor = VoiceCommandProcessor(use_mock=ctx.obj.get("debug", False))
        result = processor.process_text(text, confidence)
        
        # Display result
        click.echo("\n" + "="*60)
        click.echo("TEXT COMMAND PROCESSING RESULT")
        click.echo("="*60)
        
        if result["status"] == "success":
            click.secho("✓ Command Generated Successfully", fg="green", bold=True)
            click.echo(f"\nInput Text: {result['transcribed_text']}")
            click.echo(f"Detected Intent: {result['intent']}")
            click.echo(f"Confidence: {result['confidence']:.2%}")
            click.echo("\nGenerated Command:")
            command_json = result["command"]
            click.echo(json.dumps(command_json, indent=2) if pretty else json.dumps(command_json))
            
            # Save to file if requested
            if output:
                with open(output, "w") as f:
                    json.dump(command_json, f, indent=2)
                click.secho(f"\n✓ Command saved to: {output}", fg="green")
        else:
            click.secho(f"✗ {result['status'].upper()}", fg="red", bold=True)
            click.echo(f"Reason: {result.get('reason') or result.get('error', 'Unknown error')}")
        
        click.echo("="*60)
        
    except Exception as e:
        click.secho(f"✗ Failed to process text: {e}", fg="red", bold=True)
        logger.exception("Text processing failed")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status."""
    try:
        processor = VoiceCommandProcessor(use_mock=ctx.obj.get("debug", False))
        status_info = processor.get_status()
        
        click.echo("\n" + "="*60)
        click.echo("VOICE COMMAND AUTOMATION SYSTEM STATUS")
        click.echo("="*60)
        click.echo(f"Intents Loaded: {status_info['intents_loaded']}")
        click.echo(f"Commands Loaded: {status_info['commands_loaded']}")
        click.echo(f"ASR Model: {status_info['asr_model']}")
        click.echo(f"NLU Model: {status_info['nlu_model']}")
        click.echo(f"\nAuthorized Intents: {len(status_info['authorized_intents'])}")
        for intent in status_info['authorized_intents']:
            click.echo(f"  - {intent}")
        click.echo("="*60)
        
    except Exception as e:
        click.secho(f"✗ Failed to get status: {e}", fg="red", bold=True)
        logger.exception("Status check failed")
        sys.exit(1)


@cli.command()
@click.option("--intents", type=click.Path(), help="Path to intents config file")
@click.option("--commands", type=click.Path(), help="Path to commands config file")
@click.pass_context
def init_config(ctx, intents, commands):
    """Initialize configuration files."""
    try:
        # Create config directory
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Create intents config if not specified
        if not intents:
            intents = config_dir / "intents.yaml"
        
        if not Path(intents).exists():
            default_intents = """# Intent definitions for voice command system
# Each intent maps voice patterns to actions

stop_tracking:
  patterns:
    - "stop tracking"
    - "can you stop tracking"
    - "please stop tracking"
    - "stop the tracking"
  actions:
    description: "Stop tracking the air-borne system"

start_tracking:
  patterns:
    - "start tracking"
    - "begin tracking"
    - "start tracking now"
    - "please start tracking"
  actions:
    description: "Start tracking the air-borne system"

reset_system:
  patterns:
    - "reset system"
    - "system reset"
    - "please reset"
    - "reset everything"
  actions:
    description: "Reset the system to default state"

emergency_stop:
  patterns:
    - "emergency stop"
    - "emergency"
    - "stop immediately"
    - "kill engines"
  actions:
    priority: "critical"
    description: "Immediate system shutdown

increase_speed:
  patterns:
    - "increase speed"
    - "speed up"
    - "go faster"
    - "accelerate"
  actions:
    parameter: "speed"
    description: "Increase system speed"

decrease_speed:
  patterns:
    - "decrease speed"
    - "slow down"
    - "reduce speed"
    - "slower"
  actions:
    parameter: "speed"
    description: "Decrease system speed"

get_status:
  patterns:
    - "what is the status"
    - "status report"
    - "give me the status"
    - "status check"
  actions:
    description: "Get current system status"
"""
            with open(intents, "w") as f:
                f.write(default_intents)
            click.secho(f"✓ Created intents config: {intents}", fg="green")
        
        # Create commands config if not specified
        if not commands:
            commands = config_dir / "commands.yaml"
        
        if not Path(commands).exists():
            default_commands = """# Command mappings - maps intents to JSON commands
# Each command defines the action to send to the air-borne console

stop_tracking:
  command_type: "tracking"
  parameters:
    action: "stop"
    immediate: "true"
  description: "Stop tracking the target"

start_tracking:
  command_type: "tracking"
  parameters:
    action: "start"
    mode: "auto"
  description: "Start tracking the target"

reset_system:
  command_type: "system"
  parameters:
    action: "reset"
    preserve_config: "true"
  description: "Reset system to default state"

emergency_stop:
  command_type: "emergency"
  parameters:
    action: "shutdown"
    save_state: "true"
    priority: "critical"
  description: "Emergency system shutdown"

increase_speed:
  command_type: "control"
  parameters:
    action: "adjust_speed"
    adjustment: "increase"
    step: "10"
  description: "Increase operational speed"

decrease_speed:
  command_type: "control"
  parameters:
    action: "adjust_speed"
    adjustment: "decrease"
    step: "10"
  description: "Decrease operational speed"

get_status:
  command_type: "query"
  parameters:
    action: "get_status"
    include_telemetry: "true"
  description: "Request current system status
"""
            with open(commands, "w") as f:
                f.write(default_commands)
            click.secho(f"✓ Created commands config: {commands}", fg="green")
        
        click.secho("\n✓ Configuration initialized successfully", fg="green", bold=True)
        click.echo(f"Intents config: {intents}")
        click.echo(f"Commands config: {commands}")
        
    except Exception as e:
        click.secho(f"✗ Failed to initialize config: {e}", fg="red", bold=True)
        logger.exception("Config initialization failed")
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__
    click.echo(f"Voice Command Automation System v{__version__}")
    click.echo("A production-ready NLP-based voice command system for air-borne console control")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
