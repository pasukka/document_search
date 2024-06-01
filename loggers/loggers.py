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
