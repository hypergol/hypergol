import logging


class Logger:

    INFO = logging.INFO
    DEBUG = logging.DEBUG

    def __init__(self, path=None, level=logging.INFO, overWrite=False):
        if path is not None:
            path = str(path)
        self.path = path
        self.level = level
        self.overWrite = overWrite

        self._logger = logging.getLogger()
        self._logger.setLevel(level=self.level)
        handlers = self._logger.handlers.copy()
        for handler in handlers:
            self._logger.removeHandler(handler)

        handler = logging.StreamHandler(stream=None)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        handler.setLevel(level=self.level)
        self._logger.addHandler(handler)
        if self.path is not None:
            handler = logging.FileHandler(self.path, mode='w' if self.overWrite else 'a')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            handler.setLevel(level=self.level)
            self._logger.addHandler(handler)

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.path, self.level, self.overWrite)

    def exception(self, message):
        self._logger.exception(message)

    def info(self, message):
        self._logger.info(message)

    def log(self, message):
        self.info(message)
