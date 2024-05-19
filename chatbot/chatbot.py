import os
import json

from document_searcher.document_searcher import DocumentSearcher

# TODO: different strategies for searching one text or many docs
# TODO: mb add some comments
# TODO: do smth with big amount of funcs

# TODO: add legal stopping program
# TODO: take 'user_dir_path' from bot or when stopping program clean everything


class DocumentSearchBot:

    def __init__(self):
        self.doc_searcher = DocumentSearcher()
        self.docs_path = self.doc_searcher.docs_path
        self.user_dir_path = ''
        with open('metadata/metadata.json', 'r', encoding='utf-8') as file:
            self.metadata = json.load(file)

    def get_start_info(self) -> str:
        return self.metadata["info"]["start_info"]

    def get_help_info(self) -> str:
        return self.metadata["info"]["help_info"]

    def get_button_find_info(self) -> str:
        return self.metadata["button"]["button_find_info"]

    def get_button_load_file(self) -> str:
        return self.metadata["button"]["button_load_file"]

    def get_button_help(self) -> str:
        return self.metadata["button"]["button_help"]

    def get_find_message(self) -> str:
        return self.metadata["response"]["find_response"]

    def load_file_response(self) -> str:
        return self.metadata["response"]["load_file_response"]

    def waiting_for_loading_response(self) -> str:
        return self.metadata["response"]["loading_file_response"]

    def success_file_loading_response(self) -> str:
        return self.metadata["response"]["file_loaded_response"]

    def error_file_format_response(self) -> str:
        return self.metadata["error"]["error_file_format"]

    def loading_file_error_response(self) -> str:
        return self.metadata["error"]["loading_file_error"]

    def error_token_response(self) -> str:
        return self.metadata["error"]["error_token_response"]

    def unknown_error_response(self) -> str:
        return self.metadata["error"]["unknown_error_response"]

    def ask(self, message: str) -> str:
        answer = self.doc_searcher.ask(message)
        return answer

    def restart(self):
        if os.path.exists(self.user_dir_path):
            filelist = [f for f in os.listdir(self.user_dir_path)]
            try:
                for f in filelist:
                    os.remove(os.path.join(self.user_dir_path, f))
                os.rmdir(self.user_dir_path)
            except Exception:
                pass
        self.doc_searcher.restart()

    def load_file(self, chat_id, document_file_name, downloaded_file):
        self.user_dir_path = self.docs_path + 'chat_' + str(chat_id) + '/'
        if not os.path.exists(self.user_dir_path):
            os.makedirs(self.user_dir_path)
        src = self.user_dir_path + document_file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        self.doc_searcher.change_docs_path(self.user_dir_path)
