from chatbot.chatbot import DocumentSearcherBot


def main():
    chatbot = DocumentSearcherBot()
    chatbot.ask("I need a large backpack. Which one do you recommend?")
    # chatbot.ask("How much does it cost?")


if __name__ == "__main__":
    main()