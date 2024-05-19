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
        self.similarity_docs = []
        self.path = docs_path
        self.load_files()
        self.docs_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model_id,
                                                        task="feature-extraction",
                                                        huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))

    def __call__(self, user_intent: str) -> list[str]:
        similar_docs = self.search_docs(user_intent)
        context_list = [doc.page_content for doc in similar_docs]
        return context_list

    def load_files(self):
        list_of_texts = [f for f in listdir(self.path)
                         if isfile(join(self.path, f))]
        for i in range(len(list_of_texts)):
            with open(self.path + list_of_texts[i], 'r', encoding='utf-8') as file:
                text = file.read()
                self.similarity_docs.append({"id": i, "text": text})
        df = pd.DataFrame(self.similarity_docs)
        df.head()

        loader = DataFrameLoader(df, page_content_column='text')
        documents = loader.load()

        # TODO: change to summarization
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        # making db
        # TODO: mb save somewhere
        self.db = FAISS.from_documents(texts, self.docs_embeddings)
        self.db.as_retriever()

    def search_docs(self, query: str):
        embedding_vector = self.docs_embeddings.embed_query(query)
        similarity_search = self.db.similarity_search_by_vector(
            embedding_vector)
        return similarity_search
