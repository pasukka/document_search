from document_searcher.document_searcher import DocumentSearcher


def main():
    chatbot = DocumentSearcher()
    chatbot.ask("Мне нужен большой рюкзак. Какой бы ты посоветовал?")
    # chatbot.ask("How much does it cost?")


if __name__ == "__main__":
    main()