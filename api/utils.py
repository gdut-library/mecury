#coding: utf-8

import requests as _requests
from requests.exceptions import (
    RequestException, HTTPError, ConnectionError
)

from .exceptions import LibraryNetworkError


__all__ = ['requests']


class RequestsProxy(object):

    def __getattr__(self, name):
        attr = getattr(_requests, name)

        # 确保 `attr` 是可调用的
        if attr and getattr(attr, '__call__'):

            def wrapper(*args, **kwargs):
                '''`requests` 抛出网络异常的时候，
                用 `LibraryNetworkError` 代替
                '''

                try:
                    return attr(*args, **kwargs)
                except (RequestException, HTTPError, ConnectionError):
                    raise LibraryNetworkError

            return wrapper
        elif attr:
            return attr
        else:
            raise AttributeError


requests = RequestsProxy()
