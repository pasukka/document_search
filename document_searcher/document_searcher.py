import os
import requests
import urllib3.exceptions
from urllib3.exceptions import ReadTimeoutError
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from document_searcher.intent_summarizer import IntentSummarizer
from document_searcher.context_retriever import ContextRetriever
from document_searcher.config import load_config

USER = "user"
ASSISTANT = "assistant"
# TODO: tests

# TODO: strange answers (adds "user"; does not answer if thanks or adds more unnecessary info)


class DocumentSearcher:
    hf_token: str

    def __init__(self):
        load_dotenv()
        self.chat_history = []
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.config = load_config('config.yml')
        self.model = self.config.llm
        self.docs_path = self.config.docs_path
        self.log_messages = self.config.log_messages
        self.llm = InferenceClient(model=self.model,
                                   timeout=100,
                                   token=self.hf_token)
        self.intent_summarizer = IntentSummarizer()
        self.context_retriever = ContextRetriever(self.docs_path)
        self.error_code = 0

        with open("./prompts/find_answer.txt", 'r', encoding='utf-8') as file:
            self.prompt_template = file.read()

    def _summarize_user_intent(self, query: str) -> str:
        intent = self.intent_summarizer(query, self._make_str_chat_history())
        return intent

    def _get_context(self, user_intent: str) -> list[str]:
        documents_context_list = self.context_retriever(user_intent)
        return documents_context_list

    def _get_model_answer(self, documents_context_list: list[str]) -> str:
        prompt = self.prompt_template.replace('{chat_history}',
                                              self._make_str_chat_history())
        prompt = prompt.replace('{context}', f"\n{documents_context_list}")
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=300,
                                            temperature=0.2).strip()
        return response

    def _make_str_chat_history(self) -> str:
        chat_history_str = ""
        for message in self.chat_history:
            chat_history_str += f"{message['role']}: {message['content']}\n"
        return chat_history_str

    def ask(self, query: str) -> str:
        response = ""
        try:
            if self.log_messages:
                print("Finding best answer ...\n")
                print("---------------\n"
                      f"[QUESTION]: {query}\n")

            user_intent = self._summarize_user_intent(query)
            if self.log_messages:
                print(f"[USER INTENT]: {user_intent}\n")

            documents_context_list = self._get_context(user_intent)
            user_message = {"role": USER, "content": query}
            self.chat_history.append(user_message)

            response = self._get_model_answer(documents_context_list)
            if self.log_messages:
                print(f"[RESPONSE]: {response}\n"
                      "---------------\n")

            assistant_message = {"role": ASSISTANT, "content": response}
            self.chat_history.append(assistant_message)
        except requests.exceptions.ReadTimeout or ReadTimeoutError or urllib3.exceptions.ReadTimeoutError or TimeoutError as e:
            self.error_code = 1
            print(self.error_code, e)
        except ValueError as e:
            self.error_code = 2
            print(self.error_code, e)
        except Exception as e:
            self.error_code = 3
            print(self.error_code, e)
        return response

    def restart(self):
        self.chat_history = []
        self.docs_path = self.config.docs_path

    def change_docs_path(self, new_docs_path=''):
        if new_docs_path == '':
            new_docs_path = self.config.docs_path
        self.context_retriever = ContextRetriever(
            new_docs_path, load_from_db=False)
