from typing import Self
# from transformers import AutoTokenizer, AutoModel
# import torch
# import torch.nn.functional as F
from os import listdir
from os.path import isfile, join

MIN_SIMILARITY = 0.3


class ContextRetriever:
    model_id = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    similarity_docs: list
    docs: list

    def __init__(self):
        super().__init__()
        # self.bert = AutoModel.from_pretrained(self.model_id)
        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.similarity_docs = []
        self.docs = []
        path = "./documents/"
        list_of_texts = [f for f in listdir(path) if isfile(join(path, f))]

        for i in range(len(list_of_texts)):
            with open(path + list_of_texts[i], 'r', encoding='utf-8') as file:
                text = file.read()
                self.docs.append({"id": i, "text": text})

    # def vectorize_user_intent(self, text: str) -> list[float]:
    #     input_ids = self.tokenizer(text, return_tensors='pt')['input_ids']
    #     with torch.inference_mode():
    #         result = self.forward(input_ids).squeeze()
    #     values = [n.item() for n in result]
    #     return values

    # def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
    #     # [N, 768]
    #     token_embeddings = self.bert(input_ids)[0]

    #     # [1, 768]
    #     token_embeddings_sums = torch.sum(token_embeddings, 1)

    #     return F.normalize(token_embeddings_sums, p=2, dim=1)

    def __call__(self, user_intent: str) -> list[str]:
        # query_vector = self.vectorize_user_intent(user_intent)
        # self.search_docs(query_vector)
        # context_list = [doc["content"] for doc in self.similarity_docs]
        # return context_list
        return ['Большой рюкзак продается в Спортмастере', 'Рюкзак Maybe One стоимостью 8 тыс. руб.']

    def calculate_similarity(self, query_vector: list[float], doc_vector: list[float]) -> float:
        res = 0
        for a, b in zip(query_vector, doc_vector):
            res += a * b
        return res

    def search_docs(self, query_vector: list[float]):
        for doc in self.docs:
            similarity = self.calculate_similarity(query_vector, doc.vector())

            if similarity < MIN_SIMILARITY:
                continue

            self.similarity_docs.append(doc)



