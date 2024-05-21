from document_searcher.document_searcher import DocumentSearcher


def main():
    chatbot = DocumentSearcher()
    chatbot.ask("Мне нужен большой надувной матрас. Какой бы ты посоветовал?")
    chatbot.ask("Расскажи что-нибудь интересное.")
    chatbot.ask("А что еще интересное знаешь?")
    chatbot.ask("Расскажи про котиков")
    chatbot.ask("Расскажи что-нибудь интересное.") # TODO gets code 3; need to to find a good way for fixing
    chatbot.ask("А что еще интересное знаешь?")
    chatbot.ask("Расскажи про котиков")


if __name__ == "__main__":
    main()