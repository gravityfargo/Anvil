import logging
import logging.config


class Logger:
    @staticmethod
    def setup_logger(config):
        logging.config.dictConfig(config)

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)
