import os
from huggingface_hub import InferenceClient
from document_searcher.config import load_config

# TODO: work with intent more for less hallucinating 

class IntentSummarizer:
    hf_token: str
    model: str

    def __init__(self):
        self.hf_token = os.getenv('HUGGINGFACE_INTENT_TOKEN')
        config = load_config('config.yml')
        self.model = config.llm
        self.llm = InferenceClient(model=self.model,
                                   timeout=8,
                                   token=self.hf_token)
        with open("./prompts/user_intent.txt", 'r', encoding='utf-8') as file:
            self.prompt_template = file.read()

    def __call__(self, query: str, chat_history: str) -> str:
        prompt = self.prompt_template.replace('{chat_history}', chat_history)
        prompt = prompt.replace('{query}', query)
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            max_new_tokens=100).strip()
        return response
