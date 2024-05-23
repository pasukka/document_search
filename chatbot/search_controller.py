import os
import json
import time
import datetime

from document_searcher.document_searcher import DocumentSearcher

MAX_RETRIES = 2


class DocumentSearcherController:

    def __init__(self):
        self.doc_searcher = DocumentSearcher()
        self.docs_path = self.doc_searcher.docs_path
        self.retries = 0
        self.log_path = "user_errors.log"
        with open('metadata/metadata.json', 'r', encoding='utf-8') as file:
            self.metadata = json.load(file)
        self.clean_all_user_dirs()

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

    def change_docs_path(self, chat_id):
        user_dir_path = self.docs_path + 'chat_' + str(chat_id) + '/'
        self.doc_searcher.change_docs_path(user_dir_path)

    def get_path(self, chat_id):
        user_dir_path = self.docs_path + 'chat_' + str(chat_id) + '/'
        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)
        return user_dir_path

    def clean_all_user_dirs(self):
        dirlist = [f for f in os.listdir(self.docs_path)
                   if f.startswith('chat_')]
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

    def callback(self, message):
        t = datetime.datetime.now()
        with open(self.log_path, 'a+', encoding='utf-8') as f:
            f.write(f'Time:{t}\nMessage:{message}\n\n')
