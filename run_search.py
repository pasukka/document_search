from document_searcher.document_searcher import DocumentSearcher
import document_searcher


def main():
    chatbot = DocumentSearcher()
    try:
        docs_path = 'no_dir/'
        chatbot.change_docs_path(docs_path)
    except document_searcher.errors.FileError as e:
        print(e.message)
        
    chatbot.ask("Мне нужен большой надувной матрас. Какой бы ты посоветовал?")
    chatbot.ask("Расскажи что-нибудь интересное.")
    chatbot.ask("Спасибо")


if __name__ == "__main__":
    main()
