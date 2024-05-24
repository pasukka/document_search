import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings


class ContextRetriever:
    model: str
    documents_path: str

    def __init__(self, documents_path, load_from_db=True):
        self.model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.documents_path = documents_path
        self.documents_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model,
                                                             task="feature-extraction",
                                                             huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))
        self.load_data_base(load_from_db)

    def __call__(self, user_intent: str) -> list[str]:
        relevant_documents = self.find_relevant_documents(user_intent)
        documents_context_list = [
            doc.page_content for doc in relevant_documents]
        return documents_context_list

    def load_data_base(self, load_from_db=True):
        db_dir = self.documents_path
        if os.path.exists(db_dir+'index.faiss') and load_from_db:
            # loading needs allow_dangerous_deserialization
            self.db = FAISS.load_local(db_dir,
                                       self.documents_embeddings,
                                       allow_dangerous_deserialization=True)
        else:
            documents = self.load_documents()
            df = pd.DataFrame(documents)
            loader = DataFrameLoader(df, page_content_column='text')
            loaded_documents = loader.load()

            # splitting instead of summarization for having all info
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                           chunk_overlap=0)
            splitted_documents = text_splitter.split_documents(
                loaded_documents)

            self.db = FAISS.from_documents(splitted_documents,
                                           self.documents_embeddings)
            # [Document(page_content='text', metadata={id:1})]
            self.db.save_local(db_dir)

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
