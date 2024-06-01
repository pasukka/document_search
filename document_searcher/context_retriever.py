import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings

from loggers.loggers import ContextRetrieverLogger


class ContextRetriever:
    model: str
    documents_path: str

    def __init__(self, documents_path: str):
        self.model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.documents_path = documents_path
        self.logger = ContextRetrieverLogger()
        self.documents_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model,
                                                             task="feature-extraction",
                                                             huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))
        self.load_data_base(self.documents_path)

    def __call__(self, user_intent: str) -> list[str]:
        relevant_documents = self.__find_relevant_documents(user_intent)
        documents_context_list = [
            doc.page_content for doc in relevant_documents]
        self.logger.logger.info("Got relevant documents rom database.")
        return documents_context_list

    def load_data_base(self, path: str) -> None:
        if not os.path.exists(path):
            self.logger.logger.warning(f"No directory {path}.")
            raise FileNotFoundError('Директории не существует.')
        self.documents_path = path
        if os.path.exists(path+'index.faiss'):
            self.logger.logger.info("Loading database from path.")
            # loading needs allow_dangerous_deserialization
            self.db = FAISS.load_local(path,
                                       self.documents_embeddings,
                                       allow_dangerous_deserialization=True)
        else:
            self.logger.logger.info("Reloading database.")
            self.reload_db()

    def reload_db(self) -> None:
        documents = self.__load_documents(self.documents_path)
        if documents:
            try:
                df = pd.DataFrame(documents)
                loader = DataFrameLoader(df, page_content_column='text')
                loaded_documents = loader.load()
                self.logger.logger.info(
                    f"Loaded database from files from {self.documents_path}.")

                # splitting instead of summarization for having all info
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                               chunk_overlap=0)
                splitted_documents = text_splitter.split_documents(
                    loaded_documents)

                # [Document(page_content='text', metadata={id:1})]
                self.db = FAISS.from_documents(splitted_documents,
                                               self.documents_embeddings)
                self.db.save_local(self.documents_path)
                self.logger.logger.info(
                    f"Saved database to {self.documents_path}.")
            except Exception as e:
                self.logger.logger.warning(
                    f"Error while loading list of documents from {self.documents_path}.")
                self.logger.logger.debug(f"Error:{e}")
                self.logger.logger.exception(e)
        else:
            self.logger.logger.warning(
                f"Empty list of documents in {self.documents_path}.")

    def __load_documents(self, path: str) -> list[dict]:
        list_of_documents = [f for f in listdir(path)
                             if isfile(join(path, f)) and f.split('.')[1] == 'txt']
        documents = []
        for i in range(len(list_of_documents)):
            with open(path + list_of_documents[i], 'r', encoding='utf-8') as file:
                text = file.read()
                if text:
                    documents.append({"id": i, "text": text})
        self.logger.logger.info(f"Loaded files from path {path}.")
        return documents

    def __find_relevant_documents(self, query: str) -> list:
        embedding_vector = self.documents_embeddings.embed_query(query)
        relevant_docs = self.db.similarity_search_by_vector(embedding_vector)
        self.logger.logger.info(f"Found relevant documents.")
        return relevant_docs
