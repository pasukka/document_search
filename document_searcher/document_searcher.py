import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from document_searcher.intent_summarizer import IntentSummarizer
from document_searcher.context_retriever import ContextRetriever
from document_searcher.config import load_config

USER = "user"
ASSISTANT = "assistant"


class DocumentSearcher:
    hf_token: str
    chat_history = []

    def __init__(self):
        load_dotenv()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.intent_summarizer = IntentSummarizer()
        self.context_retriever = ContextRetriever()
        config = load_config('config.yml')
        self.model = config.llm
        self.llm = InferenceClient(model=self.model,
                                   timeout=8,
                                   token=self.hf_token)

    def _summarize_user_intent(self, query: str) -> str:
        intent = self.intent_summarizer(query, self._make_str_chat_history())
        return intent

    def _get_context(self, user_intent: str) -> list[str]:
        context_list = self.context_retriever(user_intent)
        return context_list

    def _get_model_answer(self, context_list: list[str]) -> str:
        prompt_path = "./prompts/find_answer.txt"
        with open(prompt_path, 'r', encoding='utf-8') as file:
            prompt = file.read()
        prompt = prompt.replace(
            '{chat_history}', self._make_str_chat_history())
        context = f"\n{context_list}"
        prompt = prompt.replace('{context}', context)
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=100).strip()
        return response

    def _make_str_chat_history(self) -> str:
        chat_history_str = ""
        for entry in self.chat_history:
            chat_history_str += f"{entry['role']}: {entry['content']}\n"
        return chat_history_str

    def ask(self, query: str) -> str:
        user_intent = self._summarize_user_intent(query)
        context_list = self._get_context(user_intent)
        user_message = {"role": USER, "content": query}
        self.chat_history.append(user_message)

        response = self._get_model_answer(context_list)
        print(
            "---------------\n"
            f"[QUESTION]: {query}\n"
            f"[USER INTENT]: {user_intent}\n"
            f"[RESPONSE]: {response}\n"
            "---------------\n"
        )
        assistant_message = {"role": ASSISTANT, "content": response}
        self.chat_history.append(assistant_message)
        return response
