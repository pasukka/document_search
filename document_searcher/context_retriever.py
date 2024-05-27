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

    def __init__(self, documents_path: str):
        self.model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        self.documents_path = documents_path
        self.documents_embeddings = HuggingFaceHubEmbeddings(repo_id=self.model,
                                                             task="feature-extraction",
                                                             huggingfacehub_api_token=os.getenv('HUGGINGFACE_EMBEDDINGS_TOKEN'))
        self.__load_data_base()

    def __call__(self, user_intent: str) -> list[str]:
        relevant_documents = self.__find_relevant_documents(user_intent)
        documents_context_list = [
            doc.page_content for doc in relevant_documents]
        return documents_context_list

    def __load_data_base(self) -> None:
        db_dir = self.documents_path
        if not os.path.exists(db_dir):
            raise FileNotFoundError('Директории не существует')
        if os.path.exists(db_dir+'index.faiss'):
            # loading needs allow_dangerous_deserialization
            self.db = FAISS.load_local(db_dir,
                                       self.documents_embeddings,
                                       allow_dangerous_deserialization=True)
        else:
            self.reload_db(db_dir)

    def reload_db(self, path: str) -> None:
        documents = self.__load_documents(path)
        self.documents_path = path
        df = pd.DataFrame(documents)
        loader = DataFrameLoader(df, page_content_column='text')
        loaded_documents = loader.load()

        # splitting instead of summarization for having all info
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=0)
        splitted_documents = text_splitter.split_documents(
            loaded_documents)

        # [Document(page_content='text', metadata={id:1})]
        self.db = FAISS.from_documents(splitted_documents,
                                       self.documents_embeddings)
        self.db.save_local(path)

    def __load_documents(self, path: str) -> list[dict]:
        list_of_documents = [f for f in listdir(path)
                             if isfile(join(path, f)) and f.split('.')[1] == 'txt']
        documents = []
        for i in range(len(list_of_documents)):
            with open(path + list_of_documents[i], 'r', encoding='utf-8') as file:
                text = file.read()
                documents.append({"id": i, "text": text})
        return documents

    def __find_relevant_documents(self, query: str) -> list:
        embedding_vector = self.documents_embeddings.embed_query(query)
        relevant_docs = self.db.similarity_search_by_vector(embedding_vector)
        return relevant_docs
