from document_searcher.document_searcher import DocumentSearcher


def test_start_ds():
    ds = DocumentSearcher()
    with open("./prompts/find_answer.txt", 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    assert ds.prompt_template == prompt_template


def test_restart():
    ds = DocumentSearcher()
    docs_path = 'documents/test_dir/'
    chat_history = 'something'
    ds.docs_path = docs_path
    ds.chat_history = chat_history
    ds.restart()
    assert ds.docs_path != docs_path
    assert ds.chat_history != chat_history


def test_change_docs_path():
    ds = DocumentSearcher()
    docs_path = 'documents/test_dir/'
    ds.change_docs_path(docs_path)
    assert ds.docs_path == docs_path
    assert ds.context_retriever.documents_path == docs_path


# TODO: ask: all exceptions, error_code

# TODO: Check model answer

# TODO: strange answers (does not answer if thanks or adds more unnecessary info)
