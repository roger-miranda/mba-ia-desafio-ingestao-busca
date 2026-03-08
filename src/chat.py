from src.search import search_prompt
from src.retrieval import orchestrate_search
from src.llm_response import orchestrate_response
from src.config import load_config, get_active_provider
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

        # Load configuration for database and provider info
        try:
            config = load_config()
            provider = get_active_provider()
            db_url = config.get("DATABASE_URL")
            collection_name = config.get("PG_VECTOR_COLLECTION_NAME")
        except ValueError as e:
            print(f"Erro ao carregar configuração: {e}")
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

                # Process the question through the pipeline
                try:
                    # Use the orchestrators directly for better control
                    search_results = orchestrate_search(
                        question=user_input,
                        provider=provider,
                        db_url=db_url,
                        collection_name=collection_name
                    )

                    response = orchestrate_response(
                        question=user_input,
                        context=search_results,
                        provider=provider
                    )

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