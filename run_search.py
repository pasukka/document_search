from document_searcher.document_searcher import DocumentSearcher


def main():
    chatbot = DocumentSearcher()
    chatbot.ask("Мне нужен большой надувной матрас. Какой бы ты посоветовал?")


if __name__ == "__main__":
    main()