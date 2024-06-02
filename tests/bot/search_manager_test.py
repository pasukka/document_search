import os
import json
import pytest
from bot.search_manager import DocumentSearcherManager
from database.database import create_chat, delete_chat, create_database, close_db
from database.errors import ChatPathError


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
    id = 0
    sm.callback(id, "some error")
    path = 'logs/callback_logger.log'
    assert os.stat(path).st_size != 0


@pytest.mark.asyncio
async def test_restart():
    sm = DocumentSearcherManager()
    id = 0
    path = 'documents/chat_0/'
    await create_database()
    await create_chat(id, 'private', path)
    await sm.restart(id)
    assert os.path.isdir(path) == False
    make_path(path)
    await delete_chat(id)
    await close_db()


@pytest.mark.asyncio
async def test_change_docs_path():
    sm = DocumentSearcherManager()
    id = 0
    path = 'documents/chat_0/'
    await create_database()
    await create_chat(id, 'private', path)
    await sm.change_docs_path(id)
    assert sm.doc_searcher.docs_path == path
    await delete_chat(id)
    await close_db()


@pytest.mark.asyncio
async def test_get_docs_list():
    sm = DocumentSearcherManager()
    id = 0
    path = 'documents/chat_0/'
    await create_database()
    await create_chat(id, 'private', path)
    filelist = await sm.get_docs_list(id)
    assert len(filelist) == 1
    await delete_chat(id)
    await close_db()


@pytest.mark.asyncio
async def test_get_path_1():
    sm = DocumentSearcherManager()
    id = 2
    path = '/documents/chat_2/'
    await create_database()
    await create_chat(id, 'private', path)
    file_path = await sm.get_path(id)
    await delete_chat(id)
    assert file_path == path
    await close_db()


@pytest.mark.asyncio
async def test_get_path_2():
    sm = DocumentSearcherManager()
    id = 2
    await create_database()
    file_path = await sm.get_path(id)
    path = './documents/chat_2/'
    default_path = './documents/'
    assert file_path != path
    assert file_path == default_path
    await close_db()


@pytest.mark.asyncio
async def test_remove_chosen_files():
    sm = DocumentSearcherManager()
    id = 0
    path = './documents/chat_0/'
    filelist = ['file.txt']
    await create_database()
    await create_chat(id, 'private', path)
    await sm.remove_chosen_files(id, filelist)
    filelist = await sm.get_docs_list(id)
    assert len(filelist) == 0
    make_path(path)
    await delete_chat(id)
    await close_db()


@pytest.mark.asyncio
async def test_remove_chosen_files_error():
    sm = DocumentSearcherManager()
    id = 0
    path = './documents/chat_0/'
    await create_database()
    await create_chat(id, 'private', path)
    filelist = ['file.txt']
    await sm.remove_chosen_files(id, filelist)
    try:
        filelist = await sm.get_docs_list(id)
    except ChatPathError:
        pass
    assert len(filelist) == 0
    make_path(path)
    await delete_chat(id)
    await close_db()


# TODO: ask
