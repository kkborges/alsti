"""
Main CLI application for Gemini Code Generator.
"""

import sys
import json
from pathlib import Path
from typing import List
import click
from loguru import logger
from rich.console import Console

from .config import get_config
from .code_generator import CodeGenerator, ProjectStep
from .code_validator import Language


console = Console()


def setup_logging(log_level: str, log_file: Path):
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=log_level, colorize=True)
    logger.add(log_file, level=log_level, rotation="10 MB")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Gemini Code Generator - Generate code using AI with automatic validation and fixing.

    This tool uses Google's Gemini AI to generate code step-by-step,
    validates each step by compiling/running the code, and automatically
    fixes errors by sending them back to the AI.
    """
    pass


@cli.command()
@click.argument("project_file", type=click.Path(exists=True))
@click.option(
    "--description",
    "-d",
    help="Project description (overrides file)",
    default=None,
)
def generate(project_file: str, description: str):
    """
    Generate a project from a JSON specification file.

    PROJECT_FILE should be a JSON file containing:
    - description: Overall project description
    - language: Default programming language
    - steps: Array of steps with name, description, language, filename, and dependencies

    Example:
    {
        "description": "Web application for sales control",
        "language": "python",
        "steps": [
            {
                "name": "Database Models",
                "description": "Create SQLAlchemy models for products, suppliers, etc.",
                "language": "python",
                "filename": "models.py",
                "dependencies": []
            }
        ]
    }
    """
    try:
        # Load configuration
        config = get_config()
        setup_logging(config.log_level, config.log_file)

        console.print("[bold]Gemini Code Generator[/bold]", style="blue")
        console.print("=" * 50 + "\n")

        # Load project specification
        with open(project_file, "r") as f:
            project_spec = json.load(f)

        project_description = description or project_spec.get("description", "")
        if not project_description:
            console.print("[red]Error: No project description provided[/red]")
            sys.exit(1)

        # Parse steps
        steps = parse_steps(project_spec.get("steps", []))
        if not steps:
            console.print("[red]Error: No steps defined in project file[/red]")
            sys.exit(1)

        # Generate project
        generator = CodeGenerator(config)
        results = generator.generate_project(project_description, steps)

        # Exit with error code if any step failed
        if any(not r.success for r in results):
            sys.exit(1)

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print(
            "\n[yellow]Hint: Copy .env.example to .env and set your GEMINI_API_KEY[/yellow]"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Fatal error")
        sys.exit(1)


@cli.command()
@click.option(
    "--description",
    "-d",
    required=True,
    help="Description of what to generate",
)
@click.option(
    "--language",
    "-l",
    type=click.Choice([lang.value for lang in Language]),
    default="python",
    help="Programming language",
)
@click.option(
    "--filename",
    "-f",
    required=True,
    help="Output filename",
)
def quick(description: str, language: str, filename: str):
    """
    Quickly generate a single file without a project specification.

    Example:
    python -m src.main quick -d "Create a REST API with Flask" -l python -f app.py
    """
    try:
        # Load configuration
        config = get_config()
        setup_logging(config.log_level, config.log_file)

        console.print("[bold]Gemini Code Generator - Quick Mode[/bold]", style="blue")
        console.print("=" * 50 + "\n")

        # Create a single step
        step = ProjectStep(
            name="Quick Generation",
            description=description,
            language=Language(language),
            filename=filename,
        )

        # Generate
        generator = CodeGenerator(config)
        results = generator.generate_project(description, [step])

        if not results[0].success:
            sys.exit(1)

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print(
            "\n[yellow]Hint: Copy .env.example to .env and set your GEMINI_API_KEY[/yellow]"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Fatal error")
        sys.exit(1)


@cli.command()
def init():
    """
    Initialize a new project by creating a .env file from .env.example.
    """
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_example.exists():
        console.print("[red]Error: .env.example not found[/red]")
        sys.exit(1)

    if env_file.exists():
        if not click.confirm(".env already exists. Overwrite?"):
            console.print("[yellow]Initialization cancelled[/yellow]")
            return

    env_example.read_text()
    env_file.write_text(env_example.read_text())

    console.print("[green]✓ Created .env file[/green]")
    console.print(
        "\n[yellow]⚠ Don't forget to edit .env and set your GEMINI_API_KEY![/yellow]"
    )
    console.print(
        "\nGet your API key at: https://makersuite.google.com/app/apikey"
    )


def parse_steps(steps_data: List[dict]) -> List[ProjectStep]:
    """
    Parse steps from JSON data.

    Args:
        steps_data: List of step dictionaries

    Returns:
        List of ProjectStep objects
    """
    steps = []
    for step_data in steps_data:
        step = ProjectStep(
            name=step_data["name"],
            description=step_data["description"],
            language=Language(step_data.get("language", "python")),
            filename=step_data["filename"],
            dependencies=step_data.get("dependencies", []),
        )
        steps.append(step)
    return steps


if __name__ == "__main__":
    cli()
