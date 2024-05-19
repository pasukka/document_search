from document_searcher.document_searcher import DocumentSearcher

# TODO: make /help;
# TODO: add that for searching only one text need to /start again (need to do for 1 or for many docs)
# TODO: for each user we need to have new name of dir f their files (by id)

# TODO: mb add some comments


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

    def restart(self):
        self.ds.restart()

    def load_file(self, document_file_name, downloaded_file):
        src = self.ds.new_docs_path + document_file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        self.ds.change_docs_path()
