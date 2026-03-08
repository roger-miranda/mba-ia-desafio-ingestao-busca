from src.search import search_prompt
from src.cli_parser import create_ai_provider_parser
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence httpx request logging
logging.getLogger("httpx").setLevel(logging.WARNING)


def main(ai_provider=None):
    """
    Main entry point for interactive CLI chat.

    Args:
        ai_provider: AI provider to use ('openai', 'google', 'mock', or None for config default)
    """
    try:
        # Initialize and display provider information
        from src.config import load_config
        from src.providers import get_ai_provider

        print("🤖 Initializing chat system...", flush=True)
        config = load_config()
        ai_provider_instance = get_ai_provider(ai_provider, config, use_fallback=True, log_selection=True)
        print("", flush=True)  # Empty line for readability

        # Interactive chat loop
        while True:
            try:
                # Display prompt and read user input
                user_input = input("Pergunta: ").strip()

                # Check for exit conditions
                if user_input.lower() in ("quit", "exit"):
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Process the question through the pipeline using search_prompt
                try:
                    response = search_prompt(user_input, ai_provider_instance)
                    # Display response
                    print(f"Resposta:\n{response}\n")

                except Exception as e:
                    logger.error(f"Erro ao processar pergunta: {e}")
                    print(f"Resposta:\nErro ao processar sua pergunta. Por favor, tente novamente.\n")

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print()
                break
            except EOFError:
                # Handle EOF (end of input stream)
                break

        # Clean exit message
        print("Chat encerrado. Obrigado!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Erro fatal no chat: {e}")
        print(f"Erro fatal: {e}", file=sys.stderr)
        sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    examples = """
Examples:
  python -m src.chat                    # Use primary provider from config
  python -m src.chat --ai openai        # Force OpenAI provider
  python -m src.chat --ai google        # Force Google provider
  python -m src.chat --ai mock          # Use mock provider for testing
        """

    parser = create_ai_provider_parser(
        "Interactive chat with RAG-powered responses",
        examples
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(ai_provider=args.ai)