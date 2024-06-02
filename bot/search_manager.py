import os
import json
import time
import datetime
import shutil

import document_searcher
from document_searcher.document_searcher import DocumentSearcher
from loggers.loggers import BotLogger, CallbackLogger, ManagerLogger
from database.database import get_files_path, get_adm_psw
from database.errors import ChatPathError, NoChatError

MAX_RETRIES = 2


class DocumentSearcherManager:

    def __init__(self):
        self.doc_searcher = DocumentSearcher()
        self.docs_path = self.doc_searcher.docs_path
        self.retries = 0
        self.bot_logger = BotLogger()
        self.manager_logger = ManagerLogger()
        self.user_feedback_logger = CallbackLogger()
        self.debug = False
        with open('metadata/metadata.json', 'r', encoding='utf-8') as file:
            self.metadata = json.load(file)
        # await self.clean_all_user_dirs()

    def get_error_message(self, error: Exception, id: int) -> str:
        error_str = ""
        if type(error) == document_searcher.errors.TimeError:
            error_str = self.metadata["error"]["error_runtime"]
            self.bot_logger.logger.error(f"Chat: {id} - RunTime error.")
            self.manager_logger.logger.error(f"Chat: {id} - RunTime error.")
        elif type(error) == document_searcher.errors.TokenError:
            error_str = self.metadata["error"]["error_token_response"]
            self.bot_logger.logger.error(
                f"Chat: {id} - Token expired. Needs changing.")
            self.manager_logger.logger.error(
                f"Chat: {id} - Token expired. Needs changing.")
        elif type(error) == document_searcher.errors.FileError:
            error_str = self.metadata["error"]["error_file"]
            self.bot_logger.logger.error(f"Chat: {id} - File error.")
            self.manager_logger.logger.error(f"Chat: {id} - File error.")
        else:
            error_str = self.metadata["error"]["unknown_error_response"]
            self.bot_logger.logger.error(f"Chat: {id} - Error: {error}.")
            self.manager_logger.logger.error(f"Chat: {id} - Error: {error}.")
        return error_str

    def ask(self, message: str, id: int) -> str:
        answer = ""
        while answer == "" and self.retries < MAX_RETRIES:
            try:
                answer = self.doc_searcher.ask(message)
                if self.debug:
                    self.manager_logger.logger.debug(f"Chat: {id} - doc_searcher answer:\n{answer}.")
                self.retries += 1
                time.sleep(4)
            except Exception as e:
                answer = self.get_error_message(e, id)
                if self.debug:
                    self.manager_logger.logger.debug(f"Chat: {id} - answer after error:\n{answer}.")
                self.manager_logger.logger.exception(e)
        self.retries = 0
        self.manager_logger.logger.info(f"Chat: {id} - Got answer from LLM.")
        return answer

    def make_user_dir(self, chat_id: int) -> str:
        return self.docs_path + 'chat_' + str(chat_id) + '/'

    async def get_user_dir(self, chat_id: int) -> str:
        path = ""
        try:
            path = (await get_files_path(chat_id))
            path = path[0] if path != None else self.docs_path
            self.bot_logger.logger.info(
                f"Chat: {chat_id} - Got user path from database.")
        except ChatPathError as e:
            self.bot_logger.logger.warning(
                f"Chat: {chat_id} - Error occurred while creating chat.")
            self.bot_logger.logger.exception(e)
        if path == "":
            self.bot_logger.logger.exception(NoChatError(chat_id))
            path = self.docs_path
        return path

    async def restart(self, chat_id: int) -> None:
        await self.clean_user_dir(chat_id)

    async def change_docs_path(self, chat_id: int) -> bool:
        changed = True
        user_dir_path = await self.get_user_dir(chat_id)
        if user_dir_path != "":
            self.doc_searcher.change_docs_path(user_dir_path)
            self.manager_logger.logger.info(f"Chat: {chat_id} - Changed documents path to {user_dir_path}.")
        else:
            changed = False
            self.manager_logger.logger.info(f"Chat: {chat_id} - Empty documents path {user_dir_path}. No changes.")
        return changed



    async def get_path(self, chat_id: int) -> str:
        user_dir_path = await self.get_user_dir(chat_id)
        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)
        self.manager_logger.logger.info(
            f"Chat: {chat_id} - Got user directory path.")
        return user_dir_path

    async def get_docs_list(self, chat_id: int) -> list[str]:
        user_dir_path = await self.get_user_dir(chat_id)
        filelist = []
        if os.path.exists(user_dir_path):
            filelist = [f for f in os.listdir(
                user_dir_path) if f.split('.')[1] == 'txt']
        self.manager_logger.logger.info(
            f"Chat: {chat_id} - Got documents list.")
        return filelist

    async def clean_all_user_dirs(self) -> None:
        dirlist = [f for f in os.listdir(self.docs_path)
                   if f.startswith('chat_')]
        self.manager_logger.logger.info(f"Starting cleaning all directories.")
        for dir in dirlist:
            await self.clean_user_dir(user_dir=self.docs_path+dir)

    async def clean_user_dir(self, chat_id=None, user_dir="") -> str:
        if chat_id != None:
            user_dir = await self.get_user_dir(chat_id)
            self.manager_logger.logger.info(
                f"Chat: {chat_id} - Got user directory: {user_dir}.")
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            self.manager_logger.logger.info(
                f"Chat: {chat_id} - Removing user directory: {user_dir}.")
        self.doc_searcher.restart()
        self.doc_searcher.change_docs_path()
        self.manager_logger.logger.info(
            f"Chat: {chat_id} - Restarting and cleaning user directory.")
        return user_dir

    async def remove_chosen_files(self, chat_id: int, filelist: list) -> str:
        user_dir = await self.get_user_dir(chat_id)
        try:
            for f in filelist:
                os.remove(os.path.join(user_dir, f))
            self.manager_logger.logger.info(
                f"Chat: {chat_id} - Removing files.")
            new_path = user_dir
            filelist = [f for f in os.listdir(user_dir)
                        if f.split('.')[1] == 'txt']
            if len(filelist) == 0:
                self.manager_logger.logger.info(
                    f"Chat: {chat_id} - Removing directory.")
                self.manager_logger.logger.debug(
                    f"Chat: {chat_id} - Directory does not contain files for searching.")
                self.doc_searcher.restart()
                new_path = self.doc_searcher.docs_path
                shutil.rmtree(user_dir)
            self.doc_searcher.change_docs_path(new_path)
            self.manager_logger.logger.info(
                f"Chat: {chat_id} - Removed directory.")
        except Exception as e:
            self.manager_logger.logger.error(
                f"Chat: {chat_id} - Error occurred: {e}.")
            self.manager_logger.logger.exception(e)
            pass
        return user_dir

    def callback(self, chat_id: str, message: str) -> str:
        date_now = datetime.datetime.now()
        id = f"{str(chat_id)}-{str(date_now.date())}-{str(date_now.hour)}-{str(date_now.minute)}"
        self.user_feedback_logger.logger.warning(
            f'Id: {id} - Chat_id: {chat_id}\nMessage: {message}')
        self.manager_logger.logger.info(
            f"Chat: {chat_id} - Saved feedback id={id}.")
        return id

    async def check_psw(self, chat_id, psw: str) -> bool:
        return (psw == await get_adm_psw())

    def switch_to_debug(self):
        self.debug = True
        self.doc_searcher.switch_to_debug()
