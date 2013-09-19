#coding: utf-8


__all__ = ['LibraryNetworkError', 'LibraryLoginError',
           'LibraryChangePasswordError', 'LibraryLoginRequired',
           'LibraryNotFoundError']


class LibraryNetworkError(Exception):
    '''网络访问异常'''


class LibraryLoginError(Exception):
    '''图书馆登录失败'''

    def __init__(self, msg=None):
        self.msg = msg or u'登录失败'


class LibraryChangePasswordError(LibraryLoginError):
    '''需要先到图书馆激活账户

    :param next: 激活地址
    '''

    def __init__(self, next):
        super(LibraryChangePasswordError, self).__init__(u'请先进行激活')
        self.next = next


class LibraryLoginRequired(LibraryLoginError):
    '''需要登录才能继续操作'''


class LibraryNotFoundError(Exception):
    pass
