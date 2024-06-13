from document_searcher.intent_summarizer import IntentSummarizer


def test_start_is():
    intent_sum = IntentSummarizer()
    with open("./prompts/user_intent.txt", 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    assert intent_sum.prompt_template == prompt_template


def test_check_intent():
    intent_sum = IntentSummarizer()
    intent_sum.debug = True
    query = 'сколько они стоят?'
    chat_history = 'user: посоветуй ботинки\n \
                    assistant: предлагаю вам ботинки от Martin Bester'
    intent = intent_sum(query, chat_history)
    assert 'user' not in intent
    assert 'assistant' not in intent
    assert 'Ответ:' not in intent


# TODO: Check intent (maybe distance btw needed and received)
