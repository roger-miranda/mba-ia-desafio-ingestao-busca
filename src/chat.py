from src.search import search_prompt
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence httpx request logging
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    """
    Main entry point for interactive CLI chat.

    Initializes the search chain and runs an interactive loop where users
    can ask questions and receive responses. Handles clean exit on 'quit' or 'exit'.
    """
    try:
        # Initialize the search chain
        chain = search_prompt()

        if not chain:
            print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            sys.exit(1)

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
                    response = chain(user_input)
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


if __name__ == "__main__":
    main()