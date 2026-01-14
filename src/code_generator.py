"""
Code generator that orchestrates the generation, validation, and fixing process.
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .gemini_client import GeminiClient
from .code_validator import CodeValidator, Language, ValidationResult


@dataclass
class ProjectStep:
    """Represents a step in the project generation."""

    name: str
    description: str
    language: Language
    filename: str
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class GenerationResult:
    """Result of code generation for a step."""

    step: ProjectStep
    code: str
    validation_result: ValidationResult
    attempts: int
    success: bool


class CodeGenerator:
    """Orchestrates code generation with validation and error fixing."""

    def __init__(self, config: Config):
        """
        Initialize code generator.

        Args:
            config: Application configuration
        """
        self.config = config
        self.gemini_client = GeminiClient(config)
        self.validator = CodeValidator(config)
        self.console = Console()

    def generate_project(
        self, project_description: str, steps: List[ProjectStep]
    ) -> List[GenerationResult]:
        """
        Generate a complete project by executing steps in order.

        Args:
            project_description: Overall project description
            steps: List of steps to execute

        Returns:
            List of generation results
        """
        logger.info(f"Starting project generation: {project_description}")
        self.console.print(
            f"\n[bold blue]🚀 Starting project generation[/bold blue]"
        )
        self.console.print(f"[dim]Project: {project_description}[/dim]\n")

        results = []
        generated_code = {}  # Store generated code for context

        for idx, step in enumerate(steps, 1):
            self.console.print(
                f"[bold cyan]Step {idx}/{len(steps)}: {step.name}[/bold cyan]"
            )
            self.console.print(f"[dim]{step.description}[/dim]")

            result = self._generate_step(
                step, project_description, generated_code
            )
            results.append(result)

            if result.success:
                generated_code[step.filename] = result.code
                self._save_code(step.filename, result.code)
                self.console.print(
                    f"[green]✓ {step.name} completed successfully "
                    f"({result.attempts} attempt(s))[/green]\n"
                )
            else:
                self.console.print(
                    f"[red]✗ {step.name} failed after "
                    f"{result.attempts} attempts[/red]\n"
                )
                logger.error(
                    f"Failed to generate {step.name}: "
                    f"{result.validation_result.error_message}"
                )
                # Continue with other steps even if one fails
                # You may want to break here depending on dependencies

        self._print_summary(results)
        return results

    def _generate_step(
        self,
        step: ProjectStep,
        project_description: str,
        generated_code: Dict[str, str],
    ) -> GenerationResult:
        """
        Generate code for a single step with retry logic.

        Args:
            step: Step to generate
            project_description: Overall project description
            generated_code: Previously generated code for context

        Returns:
            GenerationResult
        """
        context = self._build_context(
            project_description, step, generated_code
        )

        code = None
        validation_result = None
        previous_error = None

        for attempt in range(1, self.config.max_retry_attempts + 1):
            if attempt > 1:
                self.console.print(
                    f"[yellow]  ↻ Retry {attempt}/{self.config.max_retry_attempts}[/yellow]"
                )

            try:
                # Generate code
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    progress.add_task(description="  Generating code...", total=None)
                    code = self.gemini_client.generate_code(
                        step.description, context, previous_error
                    )

                # Extract code if wrapped in markdown
                code = self.gemini_client.extract_code_from_response(code)

                # Validate code
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    progress.add_task(description="  Validating code...", total=None)
                    validation_result = self.validator.validate(
                        code, step.language, step.filename
                    )

                if validation_result.success:
                    return GenerationResult(
                        step=step,
                        code=code,
                        validation_result=validation_result,
                        attempts=attempt,
                        success=True,
                    )
                else:
                    previous_error = validation_result.error_message
                    self.console.print(
                        f"[yellow]  ⚠ Validation error: "
                        f"{validation_result.error_message[:100]}...[/yellow]"
                    )

            except Exception as e:
                logger.error(f"Error in attempt {attempt}: {e}")
                previous_error = str(e)
                self.console.print(f"[red]  ✗ Error: {str(e)[:100]}...[/red]")

        # All attempts failed
        return GenerationResult(
            step=step,
            code=code or "",
            validation_result=validation_result or ValidationResult(False, "All attempts failed"),
            attempts=self.config.max_retry_attempts,
            success=False,
        )

    def _build_context(
        self,
        project_description: str,
        step: ProjectStep,
        generated_code: Dict[str, str],
    ) -> str:
        """
        Build context for code generation.

        Args:
            project_description: Overall project description
            step: Current step
            generated_code: Previously generated code

        Returns:
            Context string
        """
        parts = [f"Project: {project_description}"]

        # Add dependency code if available
        if step.dependencies:
            parts.append("\n### Related Files:")
            for dep in step.dependencies:
                if dep in generated_code:
                    parts.append(f"\n#### {dep}:")
                    parts.append(f"```{step.language}")
                    parts.append(generated_code[dep])
                    parts.append("```")

        return "\n".join(parts)

    def _save_code(self, filename: str, code: str):
        """
        Save generated code to file.

        Args:
            filename: Output filename
            code: Code content
        """
        output_path = self.config.generated_code_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code)
        logger.info(f"Saved code to {output_path}")

    def _print_summary(self, results: List[GenerationResult]):
        """
        Print summary of generation results.

        Args:
            results: List of generation results
        """
        self.console.print("\n[bold]📊 Generation Summary[/bold]")
        self.console.print("=" * 50)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        self.console.print(f"Total steps: {len(results)}")
        self.console.print(f"[green]Successful: {successful}[/green]")
        self.console.print(f"[red]Failed: {failed}[/red]")

        if failed > 0:
            self.console.print("\n[bold red]Failed steps:[/bold red]")
            for result in results:
                if not result.success:
                    self.console.print(f"  - {result.step.name}")
                    if result.validation_result.error_message:
                        self.console.print(
                            f"    Error: {result.validation_result.error_message[:200]}"
                        )

        self.console.print(
            f"\n[dim]Generated files saved to: {self.config.generated_code_dir}[/dim]"
        )
