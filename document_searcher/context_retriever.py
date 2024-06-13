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
        self.logger.info("Got relevant documents from database.")
        if self.debug:
            self.logger.debug(f"USER INTENT: {user_intent}")
            self.logger.debug(f"RELEVANT DOCS: {relevant_documents}")
            self.logger.debug(f"CONTEXT: {documents_context_list}")
        return documents_context_list

    def load_data_base(self, path: str) -> None:
        if not os.path.exists(path):
            self.logger.warning(f"No directory {path}.")
            raise FileNotFoundError(f'Директории {path} не существует.')
        self.documents_path = path
        if not self.find_database(path):
            self.logger.info("Reloading database.")
            self.reload_db()
        else:
            self.logger.info(f"Loading database from {path}.")
            # loading needs allow_dangerous_deserialization
            self.db = FAISS.load_local(path,
                                       self.documents_embeddings,
                                       allow_dangerous_deserialization=True)

    def reload_db(self) -> None:
        documents = self.__load_texts(self.documents_path)
        if documents:
            try:
                splitted_documents = self.__load_and_split_documents(documents)
                self.db = FAISS.from_documents(splitted_documents,
                                               self.documents_embeddings)
                self.db.save_local(self.documents_path)
                self.logger.info(
                    f"Saved database to {self.documents_path}.")
            except Exception as e:
                self.logger.warning(
                    f"Error while loading list of documents from {self.documents_path}.")
                self.logger.debug(f"Error:{e}")
                self.logger.exception(e)
        else:
            self.logger.warning(
                f"Empty list of documents in {self.documents_path}.")

    def __load_texts(self, path: str) -> list[dict]:
        list_of_documents = [f for f in listdir(path)
                             if isfile(join(path, f)) and f.split('.')[1] == 'txt']
        documents = []
        for i in range(len(list_of_documents)):
            doc_name = list_of_documents[i]
            with open(path + doc_name, 'r', encoding='utf-8') as file:
                text = file.read()
                if text:
                    documents.append({"name": doc_name, "text": text})
        self.logger.info(f"Loaded files from path {path}.")
        return documents

    def __find_relevant_documents(self, query: str) -> list:
        embedding_vector = self.documents_embeddings.embed_query(query)
        relevant_docs = self.db.similarity_search_with_score_by_vector(
            embedding_vector)
        result_list = [doc for doc in relevant_docs if doc[1] < MAX_SCORE]
        if len(result_list) == 0:
            result_list.append(relevant_docs[0])
            self.logger.info(
                f"After reducing by max result list became empty. Adding first text from relevant documents.")
        self.logger.info(f"Found relevant documents.")
        return result_list

    def find_database(self, path: str) -> bool:
        return os.path.exists(path+'index.faiss')

    def __load_and_split_documents(self, documents: list[dict]) -> list:
        df = pd.DataFrame(documents)
        loader = DataFrameLoader(df, page_content_column='text')
        loaded_documents = loader.load()
        self.logger.info(
            f"Loaded documents from files from {self.documents_path}.")

        # splitting instead of summarization for having all info
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=0)
        splitted_documents = text_splitter.split_documents(
            loaded_documents)
        return splitted_documents

    async def add_document(self, path: str, file_name: str) -> bool:
        self.documents_path = path
        added = True
        if not self.find_database(path):
            self.logger.info("Reloading database.")
            self.reload_db()
        else:
            try:
                documents = []
                with open(path+file_name, 'r', encoding='utf-8') as file:
                    text = file.read()
                    if text:
                        documents.append({"name": file_name, "text": text})
                self.logger.info(f"Loaded file {file_name}.")

                splitted_documents = self.__load_and_split_documents(documents)
                self.db.add_documents(splitted_documents)
                self.logger.info(
                    f"Added document doc_path to {self.documents_path}.")
                self.db.save_local(self.documents_path)
                self.logger.info(
                    f"Saved database to {self.documents_path}.")
            except Exception as e:
                self.logger.exception(e)
                added = False
        return added

    def database_to_df(self):
        v_dict = self.db.docstore._dict
        data_rows = []
        for k in v_dict.keys():
            doc_name = v_dict[k].metadata['name']
            content = v_dict[k].page_content
            data_rows.append({"id": k, "name": doc_name,
                              "content": content})
        vector_df = pd.DataFrame(data_rows)
        return vector_df

    def find_db_doc(self, df_db, document_name: str) -> str:
        # print(df_db)
        return df_db.loc[df_db['name'] == document_name]['id'].tolist()

    def delete_documents(self, documents: list) -> bool:
        deleted = True
        df_db = self.database_to_df()
        id_to_remove = []
        try:
            for doc in documents:
                id_to_remove += self.find_db_doc(df_db, doc)
            # print("IDS: ", id_to_remove)
            if id_to_remove:
                self.db.delete(id_to_remove)
            # print(self.database_to_df())
        except Exception as e:
            self.logger.exception(e)
            deleted = False
            raise e
        return deleted
