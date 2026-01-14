#!/usr/bin/env python3
"""
Quick test to verify the setup is working correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src import config
        from src import gemini_client
        from src import code_validator
        from src import code_generator
        from src import main
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are installed."""
    print("\nTesting dependencies...")
    required = [
        'google.generativeai',
        'dotenv',
        'click',
        'colorama',
        'rich',
        'pydantic',
        'loguru',
    ]

    all_ok = True
    for module in required:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - NOT INSTALLED")
            all_ok = False

    return all_ok

def test_files():
    """Test that required files exist."""
    print("\nTesting file structure...")
    required_files = [
        '.env.example',
        'README.md',
        'requirements.txt',
        'src/__init__.py',
        'src/main.py',
        'src/config.py',
        'src/gemini_client.py',
        'src/code_validator.py',
        'src/code_generator.py',
        'examples/simple_calculator.json',
        'examples/sales_control_system.json',
    ]

    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_ok = False

    return all_ok

def test_env():
    """Test .env configuration."""
    print("\nTesting .env configuration...")
    env_file = Path('.env')

    if not env_file.exists():
        print("  ⚠  .env file not found (expected for first run)")
        print("  Run: python -m src.main init")
        return True  # Not a critical error for fresh install

    content = env_file.read_text()
    if 'your_gemini_api_key_here' in content or 'GEMINI_API_KEY=' not in content:
        print("  ⚠  GEMINI_API_KEY not set in .env")
        print("  Edit .env and add your API key")
        return True  # Not a critical error for testing

    print("  ✓ .env file configured")
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("Gemini Code Generator - Setup Test")
    print("=" * 50)
    print()

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("File Structure", test_files()))
    results.append(("Environment", test_env()))

    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")

    all_passed = all(passed for _, passed in results)

    print()
    if all_passed:
        print("✅ All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Make sure .env is configured with your GEMINI_API_KEY")
        print("2. Try running: python -m src.main --help")
        print("3. Run an example: python -m src.main generate examples/simple_calculator.json")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
