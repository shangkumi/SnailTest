#coding:utf-8
import logging
import logging.handlers
import os
from config import Config

class LOG:
    logger = None
    @staticmethod
    def getLogger():
        if LOG.logger is not None:
            return LOG.logger
        LOG.logger = logging.getLogger()
        LOG.logger.setLevel(Config.LOG_LEVEL)
        Rthandler = logging.handlers.RotatingFileHandler(
                Config.LOG_FILE_PATH,
                maxBytes=Config.LOG_MAX_SIZE,
                backupCount=Config.LOG_BACKUP_COUNT,
                )
        StreamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s-[%(levelname)s][%(module)s][%(funcName)s]-%(message)s')
        Rthandler.setFormatter(formatter)
        StreamHandler.setFormatter(formatter)
        Rthandler.setLevel(Config.FILE_LOG_LEVEL)
        StreamHandler.setLevel(Config.STREAM_LOG_LEVEL)
        LOG.logger.addHandler(Rthandler)
        LOG.logger.addHandler(StreamHandler)
        return LOG.logger

Log = LOG.getLogger()

