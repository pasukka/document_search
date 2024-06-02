import os
import requests
import urllib3.exceptions
from urllib3.exceptions import ReadTimeoutError
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from document_searcher.intent_summarizer import IntentSummarizer
from document_searcher.context_retriever import ContextRetriever
from document_searcher.errors import TokenError, TimeError, FileError
from document_searcher.config import load_config
from loggers.loggers import SearcherLogger

USER = "user"
ASSISTANT = "assistant"


class DocumentSearcher:
    _hf_token: str

    def __init__(self):
        load_dotenv()
        self.chat_history = []
        self._hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.config = load_config('config.yml')
        self.model = self.config.llm
        self.docs_path = self.config.docs_path
        self.debug = self.config.debug_mode
        self.llm = InferenceClient(model=self.model,
                                   timeout=100,
                                   token=self._hf_token)
        self.intent_summarizer = IntentSummarizer()
        self.context_retriever = ContextRetriever(self.docs_path)
        self.error_code = 0
        self.searcher_logger = SearcherLogger()

        with open("./prompts/find_answer.txt", 'r', encoding='utf-8') as file:
            self.prompt_template = file.read()

    def _summarize_user_intent(self, query: str) -> str:
        intent = self.intent_summarizer(query, self._make_str_chat_history())
        self.searcher_logger.logger.info("Summarized user intent")
        if self.debug:
            self.searcher_logger.logger.debug(f"INTENT: {intent}")
        return intent

    def _get_context(self, user_intent: str) -> list[str]:
        documents_context_list = self.context_retriever(user_intent)
        self.searcher_logger.logger.info("Got context from document database")
        if self.debug:
            self.searcher_logger.logger.debug(
                f"CONTEXT: {documents_context_list}")
        return documents_context_list

    def _get_model_answer(self, documents_context_list: list[str]) -> str:
        prompt = self.prompt_template.replace('{chat_history}',
                                              self._make_str_chat_history())
        prompt = prompt.replace('{context}', f"\n{documents_context_list}")
        self.searcher_logger.logger.info(
            "Customized prompt for extracting answer from documents.")
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=300,
                                            temperature=0.2).strip()
        self.searcher_logger.logger.info("Got LLM response.")
        if self.debug:
            self.searcher_logger.logger.debug(f"RESPONSE: {response}")
        return response

    def _make_str_chat_history(self) -> str:
        chat_history_str = ""
        for message in self.chat_history:
            chat_history_str += f"{message['role']}: {message['content']}\n"
        self.searcher_logger.logger.info("Made str from chat_history.")
        return chat_history_str

    def ask(self, query: str) -> str:
        response = ""
        try:
            if self.debug:
                self.searcher_logger.logger.debug(f"QUERY: {query}")

            user_intent = self._summarize_user_intent(query)
            documents_context_list = self._get_context(user_intent)
            user_message = {"role": USER, "content": query}
            self.chat_history.append(user_message)
            if self.debug:
                self.searcher_logger.logger.debug(
                    f"CHAT_HISTORY: {self.chat_history}")

            response = self._get_model_answer(documents_context_list)
            assistant_message = {"role": ASSISTANT, "content": response}
            self.chat_history.append(assistant_message)
        except requests.exceptions.ReadTimeout or ReadTimeoutError or urllib3.exceptions.ReadTimeoutError or TimeoutError as e:
            self.error_code = 1
            self.searcher_logger.logger.error("RunTime error.")
            self.searcher_logger.logger.exception(e)
            raise TimeError() from e
        except ValueError as e:
            self.error_code = 2
            self.searcher_logger.logger.error("Token expired.")
            self.searcher_logger.logger.exception(e)
            raise TokenError() from e
        return response

    def restart(self) -> None:
        self.chat_history = []
        self.docs_path = self.config.docs_path

    def change_docs_path(self, new_docs_path="") -> None:
        if new_docs_path == "":
            new_docs_path = self.config.docs_path
        try:
            self.context_retriever.load_data_base(new_docs_path)
            self.docs_path = new_docs_path
            self.searcher_logger.logger.info(
                f"Database loaded from {new_docs_path}.")
            self.chat_history = []
        except FileNotFoundError or PermissionError as e:
            self.error_code = 3
            self.searcher_logger.logger.error(
                f"Error while loading file from {new_docs_path}.")
            self.searcher_logger.logger.exception(e)
            raise FileError() from e
        except Exception as e:
            self.searcher_logger.logger.exception(e)

    def switch_to_debug(self):
        self.debug = True
        self.intent_summarizer.debug = True
        self.context_retriever.debug = True
