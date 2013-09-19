#coding: utf-8

import urlparse

from .base import LIBRARY_URL
from .utils import requests
from .exceptions import LibraryLoginError, LibraryChangePasswordError


__all__ = ['LibraryWrapper', 'LibraryAuthWrapper']


class LibraryWrapper(object):
    '''对 GDUT 图书馆网站进行包装，暴露简单的调用接口。'''

    # 图书馆地址
    base_url = LIBRARY_URL

    def _build_url(self, sub):
        return urlparse.urljoin(self.base_url, sub)


class LibraryAuthWrapper(LibraryWrapper):
    '''提供图书馆登录相关接口'''

    # 登录 session cookie
    cookie_name = 'sulcmiswebpac'

    def login(self, username, password):
        '''登录图书馆。登录成功则返回 session cookie。
        假如是学生第一次登录图书馆，则抛出 `LibraryChangePasswordError`，
        否则抛出 `LibraryLoginError`

        :param username: 学生图书证号
        :param password: 学生登录密码
        '''
        dest = self._build_url('internalloginAjax.aspx')

        # 登录表单
        params = {'username': username, 'password': password}

        # 需要设置 referer 头进行识别
        headers = {'referer': dest}

        resp = requests.post(dest, data=params, headers=headers)

        if not resp.ok:
            raise LibraryLoginError(u'网络请求失败 %d' % resp.status_code)

        if resp.text == u'1':
            return dict(resp.cookies.items())
        elif resp.text == u'您的口令与证号相同，请先修改口令!':
            raise LibraryChangePasswordError(self._build_url('changepas.aspx'))
        else:
            raise LibraryLoginError(resp.text)

    def check_login(self, token):
        '''检查登录是否过期。

        :param token: 登录图书馆产生的 cookie (`sulcmiswebpac`)
        '''
        dest = self._build_url('/user/userinfo.aspx')
        cookies = {self.cookie_name: token}

        resp = requests.get(dest, cookies=cookies)

        return not resp.history
