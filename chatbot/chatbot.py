import os
from dotenv import load_dotenv


class DocumentSearcherBot:
    hf_token: str
    chat_history = []

    def __init__(self):
        load_dotenv()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')

    def _summarize_user_intent(self, query: str) -> str:
        return "The user wants to have a new backpack"

    def _get_context(self, user_intent: str) -> list[str]:
        return ['me', 'you']

    def _get_model_answer(self, context_list: list[str], query: str) -> str:
        return 'Hi'

    def ask(self, query: str) -> str:
        user_intent = self._summarize_user_intent(query)
        context_list = self._get_context(user_intent)
        response = self._get_model_answer(context_list, query)
        print(
            "---------------\n"
            f"[QUESTION]: {query}\n"
            f"[USER INTENT]: {user_intent}\n"
            f"[RESPONSE]: {response}\n"
            "---------------\n"
        )

        return response
