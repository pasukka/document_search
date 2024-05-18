from document_searcher.document_searcher import DocumentSearcher


class DocumentSearchBot:

    def __init__(self):
        self.ds = DocumentSearcher()

    def get_info(self) -> str:
        info_str = f"Добро пожаловать в бот для поиска информации по документу!\n" \
            "Если у тебя есть вопрос, задай его или нажми *Найти информацию*.\n" \
            "Для загрузки файла, по которому необходимо проводить поиск нажми *Загрузить файл*."
        return info_str

    def get_answer_message(self) -> str:
        return f'Отлично! Что необходимо найти?'

    def ask(self, message: str) -> str:
        answer = self.ds.ask(message)
        return answer
