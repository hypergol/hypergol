import os
import pickle
from unittest import TestCase
from hypergol import Logger
from pathlib import Path


class TestLogger(TestCase):

    def __init__(self, methodName):
        super(TestLogger, self).__init__(methodName=methodName)
        self.logFile = Path('testLogFile.tmp')

    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.logFile):
            os.remove(self.logFile)

    def test_pickle_logger(self):
        logger = Logger(path=self.logFile)
        newLogger = pickle.loads(pickle.dumps(logger))
        self.assertEqual(logger.__dict__, newLogger.__dict__)

    def test_logger_logs_into_files(self):
        firstMessage = 'firstMessage'
        secondMessage = 'secondMessage'
        with open(self.logFile, 'wt') as f:
            f.write(f'{firstMessage}\n')
        logger = Logger(path=self.logFile)
        logger.info(secondMessage)
        results = open(self.logFile, 'rt').read().split('\n')
        self.assertEqual(results[0], firstMessage)
        self.assertEqual(results[1].endswith(secondMessage), True)

    def test_logger_overwrites_files(self):
        firstMessage = 'firstMessage'
        secondMessage = 'secondMessage'
        with open(self.logFile, 'wt') as f:
            f.write(f'{firstMessage}\n')
        logger = Logger(path=self.logFile, overWrite=True)
        logger.info(secondMessage)
        results = open(self.logFile, 'rt').read().split('\n')
        self.assertEqual(results[0].endswith(secondMessage), True)
