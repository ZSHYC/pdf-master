#!/usr/bin/env python3
"""
PDF-Master Test Runner

This script provides a convenient way to run tests with automatic
dependency checking and report generation.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    required = ["pytest", "pytest_cov"]
    missing = []
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing missing dependencies...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing,
                check=True
            )
            print("Dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    return True


def run_tests(
    test_path: str = "tests/",
    coverage: bool = True,
    verbose: bool = True,
    html_report: bool = True,
) -> int:
    """
    Run pytest with optional coverage.
    
    Args:
        test_path: Path to test directory
        coverage: Whether to collect coverage
        verbose: Verbose output
        html_report: Generate HTML coverage report
    
    Returns:
        Exit code from pytest
    """
    cmd = [sys.executable, "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=skills/pdf/scripts",
            "--cov-report=term",
        ])
        if html_report:
            cmd.append("--cov-report=html")
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd)
    
    if coverage and html_report and result.returncode == 0:
        print("-" * 60)
        print("Coverage report generated in htmlcov/index.html")
    
    return result.returncode


def run_lint() -> int:
    """Run all linters."""
    linters = [
        (["black", "--check", "skills/pdf/scripts", "tests/"], "black"),
        (["isort", "--check", "skills/pdf/scripts", "tests/"], "isort"),
        (["flake8", "skills/pdf/scripts", "tests/", "--max-line-length=100", "--ignore=E501,W503"], "flake8"),
        (["mypy", "skills/pdf/scripts", "--ignore-missing-imports"], "mypy"),
    ]
    
    exit_code = 0
    for cmd, name in linters:
        print(f"\n{'='*60}")
        print(f"Running {name}...")
        print(f"{'='*60}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            exit_code = result.returncode
    
    return exit_code


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PDF-Master Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_tests.py                    # Run tests with coverage
    python scripts/run_tests.py --no-coverage      # Run tests without coverage
    python scripts/run_tests.py --lint             # Run linters only
    python scripts/run_tests.py --all              # Run lint and tests
        """
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage collection"
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Disable HTML coverage report"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linters instead of tests"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run both lint and tests"
    )
    parser.add_argument(
        "test_path",
        nargs="?",
        default="tests/",
        help="Path to test directory or file"
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if not check_dependencies():
        sys.exit(1)
    
    if args.all:
        # Run lint first
        lint_result = run_lint()
        if lint_result != 0:
            print("\nLint checks failed!")
            sys.exit(lint_result)
        
        print("\n" + "=" * 60)
        print("Running tests...")
        print("=" * 60)
        test_result = run_tests(
            args.test_path,
            coverage=not args.no_coverage,
            html_report=not args.no_html
        )
        sys.exit(test_result)
    
    if args.lint:
        sys.exit(run_lint())
    
    sys.exit(run_tests(
        args.test_path,
        coverage=not args.no_coverage,
        html_report=not args.no_html
    ))


if __name__ == "__main__":
    main()
