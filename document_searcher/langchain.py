import os
from os import listdir
from os.path import isfile, join
from dotenv import load_dotenv
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings

repo_id = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

documents = []

path = "./documents/"
listOfTexts = [f for f in listdir(path) if isfile(join(path, f))]

for i in range(len(listOfTexts)):
    with open(path + listOfTexts[i], 'r', encoding='utf-8') as file:
        text = file.read()
        documents.append({"id": i, "text": text})

df = pd.DataFrame(documents)
df.head()

loader = DataFrameLoader(df, page_content_column='text')
documents = loader.load()

# заменить на суммаризацию
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

load_dotenv()

# задаем векторайзер
embeddings = HuggingFaceHubEmbeddings(
    repo_id=repo_id,
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv('HUGGINGFACE_TOKEN'),
)

# создаем хранилище
db = FAISS.from_documents(texts, embeddings)
db.as_retriever()

# тестируем ретривер
for line in db.similarity_search_with_score('рюкзак за 8 тыс. руб'):
    print(line[0].page_content)
    print('\n')