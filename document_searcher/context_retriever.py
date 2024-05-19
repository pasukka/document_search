import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings

# TODO: save db somewhere and then extract info; for quickness
# TODO: try summarization instead of splitting


class ContextRetriever:
    model: str
    documents_path: str

    def __init__(self, documents_path):
        self.model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.documents_path = documents_path
        self.documents_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model,
                                                             task="feature-extraction",
                                                             huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))
        self.load_data_base()

    def __call__(self, user_intent: str) -> list[str]:
        relevant_documents = self.find_relevant_documents(user_intent)
        documents_context_list = [doc.page_content for doc in relevant_documents]
        return documents_context_list

    def load_data_base(self):
        documents = self.load_documents()
        df = pd.DataFrame(documents)
        loader = DataFrameLoader(df, page_content_column='text')
        loaded_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=0)
        splitted_documents = text_splitter.split_documents(loaded_documents)
        
        self.db = FAISS.from_documents(splitted_documents,
                                       self.documents_embeddings)

    def load_documents(self):
        list_of_documents = [f for f in listdir(self.documents_path)
                             if isfile(join(self.documents_path, f))]
        documents = []
        for i in range(len(list_of_documents)):
            with open(self.documents_path + list_of_documents[i], 'r', encoding='utf-8') as file:
                text = file.read()
                documents.append({"id": i, "text": text})
        return documents

    def find_relevant_documents(self, query: str):
        embedding_vector = self.documents_embeddings.embed_query(query)
        relevant_docs = self.db.similarity_search_by_vector(embedding_vector)
        return relevant_docs
