import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings


class ContextRetriever:
    model_id = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    similarity_docs: list
    docs: list

    def __init__(self, docs_path):
        super().__init__()
        self.similarity_docs = []
        path = docs_path
        list_of_texts = [f for f in listdir(path) if isfile(join(path, f))]

        for i in range(len(list_of_texts)):
            with open(path + list_of_texts[i], 'r', encoding='utf-8') as file:
                text = file.read()
                self.similarity_docs.append({"id": i, "text": text})

    def __call__(self, user_intent: str) -> list[str]:
        # TODO: make summarization [doc["content"] for doc in self.similarity_docs]
        context_list = self.search_docs(user_intent)
        return context_list

    def search_docs(self, query: str):
        df = pd.DataFrame(self.similarity_docs)
        df.head()

        loader = DataFrameLoader(df, page_content_column='text')
        documents = loader.load()

        # TODO: change to summarization
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        embeddings = HuggingFaceHubEmbeddings(repo_id=self.model_id,
                                              task="feature-extraction",
                                              huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))

        # making db
        # TODO: save somewhere
        db = FAISS.from_documents(texts, embeddings)
        db.as_retriever()

        embedding_vector = embeddings.embed_query(query)
        return db.similarity_search_by_vector(embedding_vector)
