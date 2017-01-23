# coding:utf-8
import json
import ssl

import requests
import mimetypes
import os

from requests.packages import urllib3

from .Log import Log

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings()

class HttpHandle:
    def __init__(self):
        self.http = requests.session()

    def get(self, url, params=[], headers={}):
        try:
            res = self.http.get(url, params=params, headers=headers, verify=False)
        except Exception as err:
            Log.error(err)
        Log.info('发送get请求: %s 服务器返回: %s' % (res.url, res.status_code))
        try:
            j_result = res.json()
            Log.info('返回json: %s' % j_result)
        except json.decoder.JSONDecodeError:
            pass
        return res

    def post(self, url, data=[], params=[], headers={}, files=[]):
        # files = [(file1_key, file1_path), (file2_key, file2_path), ...]
        try:
            multiple_files = [(key, (os.path.split(path)[-1], open(path, 'rb'), mimetypes.guess_type(path)[0])) for
                              key, path in files]
        except Exception as err:
            Log.error('读取文件失败\n错误信息: %s' % err)
            assert False
        try:
            res = self.http.post(url, data=data, params=params, headers=headers, files=multiple_files, verify=False)
        except Exception as err:
            Log.error(err)
            assert False

        Log.info('发送post请求: %s 服务器返回: %s' % (url, res.status_code))

        try:
            j_result = res.json()
            Log.info('返回json: %s' % j_result)
        except json.decoder.JSONDecodeError:
            pass
        return res
