from document_searcher.intent_summarizer import IntentSummarizer


def test_start_is():
    cr = IntentSummarizer()
    with open("./prompts/user_intent.txt", 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    assert cr.prompt_template == prompt_template


def test_check_intent():
    cr = IntentSummarizer()
    query = 'smth'
    chat_history = 'smth'
    cr(query, chat_history)

# TODO: Check intent (may be distance btw needed and received)

# TODO: strange answers (adds "user"; does not answer if thanks or adds more unnecessary info)
