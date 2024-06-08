import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings

from loggers.loggers import ContextRetrieverLogger

MAX_SCORE = 8


class ContextRetriever:
    model: str
    documents_path: str

    def __init__(self, documents_path: str):
        self.model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.documents_path = documents_path
        self.logger = ContextRetrieverLogger()
        self.debug = False
        self.documents_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model,
                                                             task="feature-extraction",
                                                             huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))
        self.load_data_base(self.documents_path)

    def __call__(self, user_intent: str) -> list[str]:
        relevant_documents = self.__find_relevant_documents(user_intent)
        documents_context_list = [
            doc[0].page_content for doc in relevant_documents]
        self.logger.logger.info("Got relevant documents from database.")
        if self.debug:
            self.logger.logger.debug(f"USER INTENT: {user_intent}")
            self.logger.logger.debug(f"RELEVANT DOCS: {relevant_documents}")
            self.logger.logger.debug(f"CONTEXT: {documents_context_list}")
        return documents_context_list

    def load_data_base(self, path: str, reload=False) -> None:
        if not os.path.exists(path):
            self.logger.logger.warning(f"No directory {path}.")
            raise FileNotFoundError(f'Директории {path} не существует.')
        self.documents_path = path
        if reload or not os.path.exists(path+'index.faiss'):
            self.logger.logger.info("Reloading database.")
            self.reload_db()
        else:
            self.logger.logger.info(f"Loading database from {path}.")
            # loading needs allow_dangerous_deserialization
            self.db = FAISS.load_local(path,
                                       self.documents_embeddings,
                                       allow_dangerous_deserialization=True)

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
            doc_name = path + list_of_documents[i]
            with open(doc_name, 'r', encoding='utf-8') as file:
                text = file.read()
                if text:
                    documents.append({"id": i, "name": doc_name, "text": text})
        self.logger.logger.info(f"Loaded files from path {path}.")
        return documents

    def __find_relevant_documents(self, query: str) -> list:
        embedding_vector = self.documents_embeddings.embed_query(query)
        relevant_docs = self.db.similarity_search_with_score_by_vector(
            embedding_vector)
        result_list = [doc for doc in relevant_docs if doc[1] < MAX_SCORE]
        if len(result_list) == 0:
            result_list.append(relevant_docs[0])
            self.logger.logger.info(
                f"After reducing by max result list became empty. Adding first text from relevant documents.")
        self.logger.logger.info(f"Found relevant documents.")
        return result_list

    async def add_document(self, doc_path) -> bool:  # TODO: add logging
        # TODO: if no db than need to make it
        added = True
        try:
            documents = []
            i = 10  # TODO: change it
            with open(doc_path, 'r', encoding='utf-8') as file:
                text = file.read()
                if text:
                    documents.append({"id": i, "name": doc_path, "text": text})
            self.logger.logger.info(f"Loaded file {doc_path}.")

            df = pd.DataFrame(documents)

            loader = DataFrameLoader(df, page_content_column='text')
            loaded_documents = loader.load()
            self.logger.logger.info(
                f"Loaded database from files from {self.documents_path}.")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                           chunk_overlap=0)
            splitted_documents = text_splitter.split_documents(
                loaded_documents)

            extension = FAISS.add_documents(splitted_documents)
            self.db.merge_from(extension)

            self.logger.logger.info(
                f"Added document doc_path to {self.documents_path}.")
            self.db.save_local(self.documents_path)
            self.logger.logger.info(
                f"Saved database to {self.documents_path}.")
        except Exception as e:
            added = False
        added = True #  TODO: delete this
        return added

    # def del_documents(self, filelist):
    #     v_dict = self.db.docstore._dict
    #     data_rows = []

    #     for file in filelist:
    #         chunck_list = vector_df.loc[vector_df['document']==document]['chunk_id'].tolist()

    #         self.db.delete(chunck_list)

    def delete_documents(self, document) -> bool:  # TODO: making it
        return True
    #     vector_df = self.store_to_df()
    #     chunck_list = vector_df.loc[vector_df['document']==document]['chunk_id'].tolist()
    #     self.db.delete(chunck_list)
