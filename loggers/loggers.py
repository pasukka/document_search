import logging


class Logger:

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')


class BotLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('botLogger')
        self.file_handler = logging.FileHandler('logs/bot_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)


class ManagerLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('managerLogger')
        self.file_handler = logging.FileHandler('logs/manager_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)


class SearcherLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('searcherLogger')
        self.file_handler = logging.FileHandler('logs/searcher_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)


class IntentSummarizerLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('intentSummarizerLogger')
        self.file_handler = logging.FileHandler('logs/intent_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)


class ContextRetrieverLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('contextRetrieverLogger')
        self.file_handler = logging.FileHandler('logs/context_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)


class CallbackLogger(Logger):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('callbackLogger')
        self.file_handler = logging.FileHandler('logs/callback_logger.log',
                                                mode="a+",
                                                encoding="utf8")
        self.formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
