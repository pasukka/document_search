import os
import json
import time

from document_searcher.document_searcher import DocumentSearcher

# TODO: do smth with big amount of funcs

MAX_RETRIES = 2


class DocumentSearchBot:

    def __init__(self):
        self.doc_searcher = DocumentSearcher()
        self.docs_path = self.doc_searcher.docs_path
        self.retries = 0
        with open('metadata/metadata.json', 'r', encoding='utf-8') as file:
            self.metadata = json.load(file)
        self.clean_all_user_dirs()

    def get_start_info(self) -> str:
        return self.metadata["info"]["start_info"]

    def get_help_info(self) -> str:
        return self.metadata["info"]["help_info"]

    def get_clean_info(self) -> str:
        return self.metadata["info"]["clean_info"]

    def get_button_find_info(self) -> str:
        return self.metadata["button"]["button_find_info"]

    def get_button_load_file(self) -> str:
        return self.metadata["button"]["button_load_file"]

    def get_button_help(self) -> str:
        return self.metadata["button"]["button_help"]

    def get_button_clean(self) -> str:
        return self.metadata["button"]["button_clean"]

    def get_find_message(self) -> str:
        return self.metadata["response"]["find_response"]

    def load_file_response(self) -> str:
        return self.metadata["response"]["load_file_response"]

    def waiting_for_loading_response(self) -> str:
        return self.metadata["response"]["loading_file_response"]

    def success_file_loading_response(self) -> str:
        return self.metadata["response"]["file_loaded_response"]

    def get_error_message(self) -> str:
        error = self.doc_searcher.error_code
        error_str = ""
        if error == 1:
            error_str = self.metadata["error"]["error_runtime"]
        elif error == 2:
            error_str = self.metadata["error"]["error_token_response"]
        else:
            error_str = self.metadata["error"]["unknown_error_response"]
        return error_str

    def error_file_format_response(self) -> str:
        return self.metadata["error"]["error_file_format"]

    def loading_file_error_response(self) -> str:
        return self.metadata["error"]["loading_file_error"]

    def ask(self, message: str) -> str:
        answer = ""
        while answer == "" and self.retries < MAX_RETRIES:
            answer = self.doc_searcher.ask(message)
            self.retries += 1
            time.sleep(4)
        if answer == "":
            answer = self.get_error_message()
        self.retries = 0
        return answer

    def restart(self, chat_id):
        user_dir_path = self.docs_path + 'chat_' + str(chat_id) + '/'
        self.clean_user_dir(user_dir_path)
        self.doc_searcher.restart()

    def load_file(self, chat_id, document_file_name, downloaded_file):
        user_dir_path = self.docs_path + 'chat_' + str(chat_id) + '/'
        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)
        src = user_dir_path + document_file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        self.doc_searcher.change_docs_path(user_dir_path)

    def clean_all_user_dirs(self):
        dirlist = [f for f in os.listdir(self.docs_path) if f.startswith('chat_')]
        for dir in dirlist:
            self.clean_user_dir(self.docs_path+dir)

    def clean_user_dir(self, user_dir):
        if os.path.exists(user_dir):
            filelist = [f for f in os.listdir(user_dir)]
            try:
                for f in filelist:
                    os.remove(os.path.join(user_dir, f))
                os.rmdir(user_dir)
            except Exception:
                pass
