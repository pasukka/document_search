import os
import json
from bot.search_manager import DocumentSearcherManager


def make_path(path):
    os.makedirs(path)
    with open(path+'file.txt', 'w', encoding='utf-8'):
        pass


def test_start_cr():
    sm = DocumentSearcherManager()
    with open("metadata/metadata.json", 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    assert sm.metadata == metadata


def test_callback():
    sm = DocumentSearcherManager()
    sm.callback("some error")
    assert os.stat(sm.log_path).st_size != 0


def test_restart():
    sm = DocumentSearcherManager()
    id = 0
    sm.restart(id)
    path = 'documents/chat_0/'
    assert os.path.isdir(path) == False
    make_path(path)


def test_change_docs_path():
    sm = DocumentSearcherManager()
    id = 0
    sm.change_docs_path(id)
    path = './documents/chat_0/'
    assert sm.doc_searcher.docs_path == path


def test_get_docs_list():
    sm = DocumentSearcherManager()
    id = 0
    filelist = sm.get_docs_list(id)
    assert len(filelist) == 1


def test_get_path():
    sm = DocumentSearcherManager()
    id = 2
    file_path = sm.get_path(id)
    path = './documents/chat_2/'
    assert file_path == path


def test_remove_chosen_files():
    sm = DocumentSearcherManager()
    id = 0
    filelist = ['file.txt']
    sm.remove_chosen_files(id, filelist)
    filelist = sm.get_docs_list(id)
    assert len(filelist) == 0
    path = './documents/chat_0/'
    make_path(path)


# TODO: ask
