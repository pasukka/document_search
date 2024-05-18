import os
import time
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from document_searcher.intent_summarizer import IntentSummarizer
from document_searcher.context_retriever import ContextRetriever
from document_searcher.config import load_config

USER = "user"
ASSISTANT = "assistant"


class DocumentSearcher:
    hf_token: str

    def __init__(self):
        load_dotenv()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        config = load_config('config.yml')
        self.model = config.llm
        self.docs_path = config.docs_path
        self.new_docs_path = './new_documents/'
        self.llm = InferenceClient(model=self.model,
                                   timeout=8,
                                   token=self.hf_token)
        self.intent_summarizer = IntentSummarizer()
        self.context_retriever = ContextRetriever(self.docs_path)
        self.chat_history = []
        prompt_path = "./prompts/find_answer.txt"
        with open(prompt_path, 'r', encoding='utf-8') as file:
            self.template_prompt = file.read()

    def _summarize_user_intent(self, query: str) -> str:
        intent = self.intent_summarizer(query, self._make_str_chat_history())
        return intent

    def _get_context(self, user_intent: str) -> list[str]:
        context_list = self.context_retriever(user_intent)
        return context_list

    def _get_model_answer(self, context_list: list[str]) -> str:
        prompt = self.template_prompt.replace('{chat_history}',
                                              self._make_str_chat_history())
        context = f"\n{context_list}"
        prompt = prompt.replace('{context}', context)

        # print('\n---- prompt ----')
        # print(prompt)
        # print('---- prompt ----\n')
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=200).strip()
        return response

    def _make_str_chat_history(self) -> str:
        chat_history_str = ""
        for entry in self.chat_history:
            chat_history_str += f"{entry['role']}: {entry['content']}\n"
        return chat_history_str

    def ask(self, query: str) -> str:
        try:
            print("Finding best answer ...\n")
            print("---------------\n"
                  f"[QUESTION]: {query}\n")
            user_intent = self._summarize_user_intent(query)
            print(f"[USER INTENT]: {user_intent}\n")

            context_list = self._get_context(user_intent)
            user_message = {"role": USER, "content": query}
            self.chat_history.append(user_message)

            response = self._get_model_answer(context_list)
            print(f"[RESPONSE]: {response}\n"
                  "---------------\n")
            assistant_message = {"role": ASSISTANT, "content": response}
            self.chat_history.append(assistant_message)
        except TimeoutError or requests.exceptions.ReadTimeout:
            time.sleep(2)
            self.ask(query)
        return response

    def restart(self):
        self.chat_history = []
        filelist = [f for f in os.listdir(self.new_docs_path)]
        try:
            for f in filelist:
                os.remove(os.path.join(self.new_docs_path, f))
        except Exception:
            pass

    def change_docs_path(self):
        self.context_retriever = ContextRetriever(self.new_docs_path)
