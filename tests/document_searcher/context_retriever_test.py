import pytest
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
    documents_path = "documents/test_dir/"
    cr = ContextRetriever(documents_path)
    assert len(cr.db.docstore._dict) == 2
    assert cr.documents_path == documents_path
    assert cr.db is not None


def test_error_reload_db():
    documents_path = "documents/test/"
    with pytest.raises(FileNotFoundError):
        cr = ContextRetriever(documents_path)
        assert cr.documents_path == documents_path

# TODO: add test for many docs

# TODO check context
