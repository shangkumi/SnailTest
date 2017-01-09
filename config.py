# coding:utf-8
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class LogConfig:
    LOG_LEVEL = 0
    LOG_FILE_PATH = os.path.join(BASE_DIR, 'log', 'Snail.log')
    LOG_MAX_SIZE = 1 * 1024 * 1024
    LOG_BACKUP_COUNT = 5
    FILE_LOG_LEVEL = 10
    STREAM_LOG_LEVEL = 20


class DBInfo:
    DUOBAO_TEST = {
        'TYPE': 'Oracle',
        'DBINFO': 'duobao_app_new/duobao_appd3M8@10.120.240.252:9538/oratest',
    }


class RedisInfo:
    REDIS_TEST = {
        'host': '10.120.241.210',
        'password': '1qaz2wsxX',
    }


class OpenId:
    USERNAME = 'zhubo'
    PASSWORD = 'zbwillD1T'
