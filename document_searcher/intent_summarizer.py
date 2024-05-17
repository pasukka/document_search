import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from document_searcher.config import load_config


class IntentSummarizer:
    hf_token: str

    def __init__(self):
        load_dotenv()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        config = load_config('config.yml')
        self.model = config.llm
        self.llm = InferenceClient(model=self.model,
                                   timeout=8,
                                   token=self.hf_token)

    def __call__(self, query: str, chat_history: str) -> str:
        prompt_path = "./prompts/user_intent.txt"
        with open(prompt_path, 'r', encoding='utf-8') as file:
            prompt = file.read()
        prompt = prompt.replace('{chat_history}', chat_history)
        prompt = prompt.replace('{query}', query)
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=100).strip()
        return response
