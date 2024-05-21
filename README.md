# ChatBot for documents search

Here is bot designed to make searching through documents *quick and easy* in Russian. Originally set up for computational linguistics and machine learning, this bot searches through 1681 articles from [Habr](habr.ru) to find what you need fast.

You can easily *upload your own files*, regardless of the topic, for the bot to search. Moreover, it's versatile enough to be used as a base for chatbots for businesses. 


## Example of how the bot works

![bot_example](images/bot_example.gif)

## Installation
Before use, you must ensure that `pipenv` is installed. If it is missing, use the following command:
```
pip install pipenv
```

Project installation:
```
pipenv install
```

For searching document using console program use:
```
pipenv run python run_prediction.py
```