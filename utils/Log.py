# coding:utf-8
import logging
import logging.handlers
from config import LogConfig


class LOG:
    logger = None

    @staticmethod
    def getLogger():
        if LOG.logger is not None:
            return LOG.logger
        LOG.logger = logging.getLogger()
        LOG.logger.setLevel(LogConfig.LOG_LEVEL)
        rotating_handler = logging.handlers.RotatingFileHandler(
            LogConfig.LOG_FILE_PATH,
            maxBytes=LogConfig.LOG_MAX_SIZE,
            backupCount=LogConfig.LOG_BACKUP_COUNT,
        )
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s-[%(levelname)s][%(module)s][%(funcName)s]-%(message)s')
        rotating_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        rotating_handler.setLevel(LogConfig.FILE_LOG_LEVEL)
        stream_handler.setLevel(LogConfig.STREAM_LOG_LEVEL)
        LOG.logger.addHandler(rotating_handler)
        LOG.logger.addHandler(stream_handler)
        return LOG.logger


Log = LOG.getLogger()
