import pytest
import os
from document_searcher.context_retriever import ContextRetriever


def test_start_cr():
    documents_path = "documents/"
    cr = ContextRetriever(documents_path)
    assert cr.documents_path == documents_path
    assert cr.db is not None


def test_error_start_cr():
    documents_path = "doc/"
    with pytest.raises(FileNotFoundError):
        cr = ContextRetriever(documents_path)
        assert cr.documents_path == documents_path


def test_reload_db():
    documents_path = "documents/chat_1/"
    cr = ContextRetriever(documents_path)
    assert len(cr.db.docstore._dict) == 2
    assert cr.documents_path == documents_path
    assert cr.db is not None


def test_error_reload_db():
    documents_path = "documents/test/"
    with pytest.raises(FileNotFoundError):
        cr = ContextRetriever(documents_path)
        assert cr.documents_path != documents_path


def test_load_documents():
    documents_path = "documents/chat_1/"
    cr = ContextRetriever(documents_path)
    user_intent = "узнать, что такое Алиса"
    with open(documents_path+"info_about_yandex_alice.txt", 'r', encoding='utf-8') as file:
        real_context = file.readlines()
    real_context = [line.replace('\n', '') for line in real_context]
    documents_context_list = cr(user_intent)
    assert documents_context_list == real_context

