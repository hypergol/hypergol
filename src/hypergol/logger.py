import logging


class Logger:
    """Helper class to manage file-based and screen-based logging"""

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    def __init__(self, path=None, level=logging.INFO, overWrite=False, enabled=True):
        """
        Parameters
        ----------
        path : str (default=None)
            Optional path to save logs into a file
        level : int (default=Logger.INFO)
            Log level of this logger
        overWrite : bool (default=False)
            Indicate if an existing log file should be overwritten or appended
        """
        self.path = path
        self.level = level
        self.overWrite = overWrite
        self.enabled = enabled

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
        self._set_logger_disabled()

    def _set_logger_disabled(self):
        self._logger.disabled = not self.enabled

    def disable(self):
        self.enabled = False
        self._set_logger_disabled()

    def enable(self):
        self.enabled = True
        self._set_logger_disabled()

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.path, self.level, self.overWrite, self.enabled)

    def log(self, message):
        """Convenience method for ``Logger.INFO`` level"""
        self.info(message)

    def critical(self, message):
        self._logger.critical(message)

    def error(self, message):
        self._logger.error(message)

    def exception(self, message):
        self._logger.exception(message)

    def warning(self, message):
        self._logger.warning(message)

    def info(self, message):
        self._logger.info(message)

    def debug(self, message):
        self._logger.debug(message)
