#!/usr/bin/env python3
"""
Test the validator skip logic for configuration files.
"""

import sys


def should_skip_validation(filename: str) -> bool:
    """
    Check if a file should skip validation (config/dependency files).
    This is a copy of the logic from code_validator.py for testing.
    """
    from pathlib import Path

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
        '.md',
        '.txt',
        '.json',
        '.yml',
        '.yaml',
        '.xml',
        '.toml',
        '.ini',
        '.cfg',
    ]

    filename_lower = filename.lower()

    # Get just the filename without path
    base_filename = Path(filename).name.lower()

    for pattern in SKIP_VALIDATION_PATTERNS:
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


def test_skip_validation():
    """Test that configuration files are skipped."""
    print("Testing validator skip logic...")
    print("=" * 50)

    # Test files that should skip validation
    skip_files = [
        'requirements.txt',
        'package.json',
        'package-lock.json',
        'Gemfile',
        'Cargo.toml',
        'composer.json',
        'README.md',
        'config.yml',
        'settings.json',
        'dependencies.txt',
        '.env',
        'Dockerfile',
    ]

    # Test files that should NOT skip validation
    validate_files = [
        'main.py',
        'app.js',
        'server.ts',
        'Main.java',
        'Program.cs',
        'index.php',
    ]

    print("\nFiles that SHOULD skip validation:")
    all_passed = True
    for filename in skip_files:
        skip = should_skip_validation(filename)
        status = "✓ PASS" if skip else "✗ FAIL"
        print(f"  {filename:30s} {status}")
        if not skip:
            all_passed = False

    print("\nFiles that should NOT skip validation:")
    for filename in validate_files:
        skip = should_skip_validation(filename)
        status = "✓ PASS" if not skip else "✗ FAIL"
        print(f"  {filename:30s} {status}")
        if skip:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(test_skip_validation())
