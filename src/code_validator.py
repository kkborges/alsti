"""
Code validator and compiler.
Validates generated code by compiling/running it and capturing errors.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional
from enum import Enum
from loguru import logger

from .config import Config


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    PHP = "php"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"


class ValidationResult:
    """Result of code validation."""

    def __init__(self, success: bool, error_message: Optional[str] = None):
        self.success = success
        self.error_message = error_message

    def __str__(self):
        if self.success:
            return "Validation successful"
        return f"Validation failed: {self.error_message}"


class CodeValidator:
    """Validates code by compiling/running it."""

    # Files that should skip validation (configuration/dependency files)
    SKIP_VALIDATION_PATTERNS = [
        'requirements.txt',
        'package.json',
        'package-lock.json',
        'composer.json',
        'composer.lock',
        'Gemfile',
        'Gemfile.lock',
        'Cargo.toml',
        'Cargo.lock',
        'go.mod',
        'go.sum',
        'pom.xml',
        'build.gradle',
        'build.gradle.kts',
        '.csproj',
        '.sln',
        '.env',
        '.env.example',
        '.gitignore',
        'Dockerfile',
        'docker-compose.yml',
        'README.md',
        '.md',  # All markdown files
        '.txt',  # All text files (unless it's a specific language file)
        '.json',  # JSON files (configuration)
        '.yml',
        '.yaml',
        '.xml',
        '.toml',
        '.ini',
        '.cfg',
    ]

    def __init__(self, config: Config):
        """
        Initialize code validator.

        Args:
            config: Application configuration
        """
        self.config = config
        self.language_paths = config.language_paths

    def should_skip_validation(self, filename: str) -> bool:
        """
        Check if a file should skip validation (config/dependency files).

        Args:
            filename: Filename to check

        Returns:
            True if validation should be skipped
        """
        filename_lower = filename.lower()

        # Get just the filename without path
        from pathlib import Path
        base_filename = Path(filename).name.lower()

        for pattern in self.SKIP_VALIDATION_PATTERNS:
            pattern_lower = pattern.lower()

            if pattern_lower.startswith('.'):
                # Extension pattern
                if filename_lower.endswith(pattern_lower):
                    return True
            else:
                # Check if pattern matches the base filename or is contained in full path
                if base_filename == pattern_lower or pattern_lower in filename_lower:
                    return True

        return False

    def validate(
        self, code: str, language: Language, filename: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate code by attempting to compile/run it.

        Args:
            code: Code to validate
            language: Programming language
            filename: Optional filename (will use temp file if not provided)

        Returns:
            ValidationResult with success status and error message if any
        """
        # Check if this file should skip validation
        if filename and self.should_skip_validation(filename):
            logger.info(f"Skipping validation for configuration file: {filename}")
            return ValidationResult(True, None)

        logger.info(f"Validating {language} code...")

        try:
            if language == Language.PYTHON:
                return self._validate_python(code, filename)
            elif language == Language.JAVASCRIPT:
                return self._validate_javascript(code, filename)
            elif language == Language.TYPESCRIPT:
                return self._validate_typescript(code, filename)
            elif language == Language.JAVA:
                return self._validate_java(code, filename)
            elif language == Language.CSHARP:
                return self._validate_csharp(code, filename)
            elif language == Language.PHP:
                return self._validate_php(code, filename)
            elif language == Language.GO:
                return self._validate_go(code, filename)
            elif language == Language.RUST:
                return self._validate_rust(code, filename)
            elif language == Language.RUBY:
                return self._validate_ruby(code, filename)
            else:
                return ValidationResult(
                    False, f"Unsupported language: {language}"
                )
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(False, str(e))

    def _run_command(
        self, command: list, input_text: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Run a command and capture output.

        Args:
            command: Command and arguments
            input_text: Optional input to pass to command

        Returns:
            Tuple of (success, output/error message)
        """
        try:
            result = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=self.config.validation_timeout,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {self.config.validation_timeout}s"
        except Exception as e:
            return False, str(e)

    def _validate_python(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate Python code."""
        python_path = self.language_paths.python or "python3"

        if filename:
            # Validate existing file
            success, output = self._run_command([python_path, "-m", "py_compile", filename])
        else:
            # Validate code string
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name

            success, output = self._run_command([python_path, "-m", "py_compile", temp_file])
            Path(temp_file).unlink()

        return ValidationResult(success, None if success else output)

    def _validate_javascript(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate JavaScript code."""
        node_path = self.language_paths.node or "node"

        if not filename:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
                f.write(code)
                filename = f.name

        # Node will parse and report syntax errors
        success, output = self._run_command([node_path, "--check", filename])

        if not filename.startswith("/tmp"):
            Path(filename).unlink(missing_ok=True)

        return ValidationResult(success, None if success else output)

    def _validate_typescript(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate TypeScript code."""
        npx_path = self.language_paths.npx or "npx"

        if not filename:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
                f.write(code)
                filename = f.name

        success, output = self._run_command([npx_path, "tsc", "--noEmit", filename])

        if not filename.startswith("/tmp"):
            Path(filename).unlink(missing_ok=True)

        return ValidationResult(success, None if success else output)

    def _validate_java(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate Java code."""
        javac_path = self.language_paths.javac or "javac"

        if not filename:
            # Extract class name from code
            import re
            match = re.search(r"public\s+class\s+(\w+)", code)
            class_name = match.group(1) if match else "Main"

            with tempfile.TemporaryDirectory() as tmpdir:
                filename = Path(tmpdir) / f"{class_name}.java"
                filename.write_text(code)

                success, output = self._run_command([javac_path, str(filename)])
        else:
            success, output = self._run_command([javac_path, filename])

        return ValidationResult(success, None if success else output)

    def _validate_csharp(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate C# code."""
        dotnet_path = self.language_paths.dotnet or "dotnet"

        with tempfile.TemporaryDirectory() as tmpdir:
            if not filename:
                filename = Path(tmpdir) / "Program.cs"
                filename.write_text(code)

            # Create a minimal project file
            csproj = Path(tmpdir) / "temp.csproj"
            csproj.write_text(
                '<?xml version="1.0" encoding="utf-8"?>'
                '<Project Sdk="Microsoft.NET.Sdk">'
                "<PropertyGroup>"
                "<OutputType>Exe</OutputType>"
                "<TargetFramework>net6.0</TargetFramework>"
                "</PropertyGroup>"
                "</Project>"
            )

            success, output = self._run_command([dotnet_path, "build", str(csproj)])

        return ValidationResult(success, None if success else output)

    def _validate_php(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate PHP code."""
        php_path = self.language_paths.php or "php"

        if filename:
            success, output = self._run_command([php_path, "-l", filename])
        else:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".php", delete=False) as f:
                f.write(code)
                temp_file = f.name

            success, output = self._run_command([php_path, "-l", temp_file])
            Path(temp_file).unlink()

        return ValidationResult(success, None if success else output)

    def _validate_go(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate Go code."""
        go_path = self.language_paths.go or "go"

        with tempfile.TemporaryDirectory() as tmpdir:
            if not filename:
                filename = Path(tmpdir) / "main.go"
                filename.write_text(code)

            success, output = self._run_command([go_path, "build", str(filename)])

        return ValidationResult(success, None if success else output)

    def _validate_rust(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate Rust code."""
        rustc_path = self.language_paths.rustc or "rustc"

        if not filename:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
                f.write(code)
                filename = f.name

        success, output = self._run_command([rustc_path, "--crate-type", "lib", filename])

        if not filename.startswith("/tmp"):
            Path(filename).unlink(missing_ok=True)

        return ValidationResult(success, None if success else output)

    def _validate_ruby(
        self, code: str, filename: Optional[str] = None
    ) -> ValidationResult:
        """Validate Ruby code."""
        ruby_path = self.language_paths.ruby or "ruby"

        if filename:
            success, output = self._run_command([ruby_path, "-c", filename])
        else:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".rb", delete=False) as f:
                f.write(code)
                temp_file = f.name

            success, output = self._run_command([ruby_path, "-c", temp_file])
            Path(temp_file).unlink()

        return ValidationResult(success, None if success else output)
