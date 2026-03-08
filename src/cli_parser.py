"""
Common CLI parser for AI provider selection.

This module provides a reusable argument parser that can be used by both
ingest.py and chat.py to support the same --ai parameter.
"""

import argparse


def create_ai_provider_parser(description: str, examples: str) -> argparse.ArgumentParser:
    """
    Create an argument parser with AI provider selection.

    Args:
        description: Description for the command
        examples: Example usage text

    Returns:
        ArgumentParser configured with --ai option
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples
    )

    parser.add_argument(
        "--ai",
        choices=["openai", "google", "mock"],
        help="AI provider to use (default: from config)"
    )

    return parser


def parse_ai_provider_args() -> argparse.Namespace:
    """
    Parse arguments for AI provider selection with default examples.

    Returns:
        Parsed arguments with ai attribute
    """
    examples = """
Examples:
  script.py                    # Use primary provider from config
  script.py --ai openai        # Force OpenAI provider
  script.py --ai google        # Force Google provider
  script.py --ai mock          # Use mock provider for testing
    """

    parser = create_ai_provider_parser("AI-powered application", examples)
    return parser.parse_args()