# coding:Utf-8
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class LogConfig:
    LOG_LEVEL = 0
    LOG_FILE_PATH = os.path.join(BASE_DIR, 'log', 'Snail.log')
    LOG_MAX_SIZE = 1 * 1024 * 1024
    LOG_BACKUP_COUNT = 5
    FILE_LOG_LEVEL = 10
    STREAM_LOG_LEVEL = 20
