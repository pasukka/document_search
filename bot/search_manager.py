import os
import json
import time
import datetime
import shutil

import document_searcher
from document_searcher.document_searcher import DocumentSearcher
from loggers.loggers import BotLogger, CallbackLogger

MAX_RETRIES = 2


class DocumentSearcherManager:

    def __init__(self):
        self.doc_searcher = DocumentSearcher()
        self.docs_path = self.doc_searcher.docs_path
        self.retries = 0
        self.bot_logger = BotLogger()
        self.user_feedback_logger = CallbackLogger()
        self.log_path = "logs/user_errors.log"
        with open('metadata/metadata.json', 'r', encoding='utf-8') as file:
            self.metadata = json.load(file)
        # self.clean_all_user_dirs()

    def get_error_message(self, error: Exception, id: int) -> str:
        error_str = ""
        if type(error) == document_searcher.errors.TimeError:
            error_str = self.metadata["error"]["error_runtime"]
            self.bot_logger.logger.error(f"Chat: {id} - RunTime error.")
        elif type(error) == document_searcher.errors.TokenError:
            error_str = self.metadata["error"]["error_token_response"]
            self.bot_logger.logger.error(f"Chat: {id} - Token expired.")
        elif type(error) == document_searcher.errors.FileError:
            error_str = self.metadata["error"]["error_file"]
            self.bot_logger.logger.error(f"Chat: {id} - File error.")
        else:
            error_str = self.metadata["error"]["unknown_error_response"]
            self.bot_logger.logger.error(f"Chat: {id} - Error: {error}.")
        return error_str

    def ask(self, message: str, id: int) -> str:
        answer = ""
        while answer == "" and self.retries < MAX_RETRIES:
            try:
                answer = self.doc_searcher.ask(message)
                self.retries += 1
                time.sleep(4)
            except Exception as e:
                answer = self.get_error_message(e, id)
        self.retries = 0
        return answer

    def _get_user_dir(self, chat_id: int) -> str:
        return self.docs_path + 'chat_' + str(chat_id) + '/'

    def restart(self, chat_id: int) -> None:
        self.clean_user_dir(chat_id)

    def change_docs_path(self, chat_id: int) -> None:
        user_dir_path = self._get_user_dir(chat_id)
        self.doc_searcher.change_docs_path(user_dir_path)

    def get_path(self, chat_id: int) -> str:
        user_dir_path = self._get_user_dir(chat_id)
        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)
        return user_dir_path

    def get_docs_list(self, chat_id: int) -> list[str]:
        user_dir_path = self._get_user_dir(chat_id)
        filelist = []
        if os.path.exists(user_dir_path):
            filelist = [f for f in os.listdir(
                user_dir_path) if f.split('.')[1] == 'txt']
        return filelist

    def clean_all_user_dirs(self) -> None:
        dirlist = [f for f in os.listdir(self.docs_path)
                   if f.startswith('chat_')]
        for dir in dirlist:
            self.clean_user_dir(user_dir=self.docs_path+dir)

    def clean_user_dir(self, chat_id=None, user_dir='') -> str:
        if chat_id != None:
            user_dir = self._get_user_dir(chat_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        self.doc_searcher.restart()
        self.doc_searcher.change_docs_path()
        return user_dir

    def remove_chosen_files(self, chat_id: int, filelist: list) -> str:
        user_dir = self._get_user_dir(chat_id)
        try:
            for f in filelist:
                os.remove(os.path.join(user_dir, f))
            new_path = user_dir
            filelist = [f for f in os.listdir(user_dir)
                        if f.split('.')[1] == 'txt']
            if len(filelist) == 0:
                self.doc_searcher.restart()
                new_path = self.doc_searcher.docs_path
                shutil.rmtree(user_dir)
            self.doc_searcher.change_docs_path(new_path)
        except Exception:
            pass
        return user_dir

    def callback(self, chat_id: str, message: str) -> str:
        date_now = datetime.datetime.now()
        id = f"{str(chat_id)}-{str(date_now.date())}-{str(date_now.hour)}-{str(date_now.minute)}"
        self.user_feedback_logger.logger.warning(
            f'Id: {id} - Chat_id: {chat_id}\nMessage: {message}\n\n')
        return id
