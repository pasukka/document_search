import os
from huggingface_hub import InferenceClient
from document_searcher.config import load_config
from loggers.loggers import IntentSummarizerLogger


class IntentSummarizer:
    _hf_token: str
    model: str
    prompt_template: str

    def __init__(self):
        self._hf_token = os.getenv('HUGGINGFACE_INTENT_TOKEN')
        config = load_config('config.yml')
        self.model = config.llm
        self.debug = False
        self.logger = IntentSummarizerLogger()
        self.llm = InferenceClient(model=self.model,
                                   timeout=100,
                                   token=self._hf_token)
        with open("./prompts/user_intent.txt", 'r', encoding='utf-8') as file:
            self.prompt_template = file.read()

    def __call__(self, query: str, chat_history: str) -> str:
        prompt = self.prompt_template.replace('{chat_history}', chat_history)
        prompt = prompt.replace('{query}', query)
        self.logger.info("Customized prompt for intent summarization.")
        response = self.llm.text_generation(prompt,
                                            do_sample=False,
                                            stop_sequences=['\n'],
                                            max_new_tokens=100).strip()
        if self.debug:
            self.logger.debug(f"QUERY: {query}")
            self.logger.debug(f"PROMPT: {prompt}")
            self.logger.debug(f"RESPONSE: {response}")
        self.logger.info("Got LLM response for intent summarization.")
        return response
