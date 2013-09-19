#coding: utf-8

import re
from datetime import datetime
from functools import update_wrapper
from pyquery import PyQuery as PQ

from .base import DATETIMEFMT
from .utils import requests
from .library import LibraryAuthWrapper
from .exceptions import (
    LibraryLoginRequired, LibraryNotFoundError, LibraryNetworkError
)

__all__ = ['Me']


def auth_required(func):
    '''进行用户验证，如果验证失败，
    将抛出 `LibraryLoginRequired` 异常。

    :param token: session token (`sulcmiswebpac`) 值
    '''
    def auth_wrapper(self, token, *args, **kwargs):
        if not self.check_login(token):
            raise LibraryLoginRequired

        # 设置 session cookie
        self.token = token
        self.cookies = {self.cookie_name: self.token}

        return func(self, *args, **kwargs)

    return update_wrapper(auth_wrapper, func)


def _convert_datetime(raw, fmt=None):
    fmt = fmt or DATETIMEFMT

    return datetime.strptime(raw, fmt)


class Me(LibraryAuthWrapper):
    '''学生信息接口'''

    # session cookie 值
    token = None

    # 请求 cookie
    cookies = None

    def _get_details(self, books, getter=None, setter=None):
        '''获取书籍详细信息

        :param books: 书籍列表
        :param getter: 从书籍信息里获取 ctrlno
        :param setter: 设置书籍详细信息
        '''
        from .book import Book

        def _getter(x):
            return x['ctrlno']

        def _setter(x, y):
            x['details'] = y

        getter = getter or _getter
        setter = setter or _setter
        book = Book()

        for i in books:
            setter(i, book.get(getter(i)))

        return books

    @auth_required
    def personal(self):
        '''获取个人信息

        个人信息包括：

        - 校园卡卡号 cardno
        - 姓名 name
        - 学院单位 faculty
        - 专业 major
        - 读者类型 reader_type
        - 读者状态 reader_status
        '''

        def parse_infos(pq):
            infos = pq('.inforight')
            return {
                'cardno': PQ(infos[0]).text().strip(),
                'name': PQ(infos[1]).text().strip(),
                'faculty': PQ(infos[3]).text().strip(),
                'major': PQ(infos[7]).text().strip(),
                'reader_type': PQ(infos[2]).text().strip(),
                'reader_status': PQ(infos[4]).text().strip()
            }

        dest = self._build_url('/user/userinfo.aspx')

        resp = requests.get(dest, cookies=self.cookies)
        q = PQ(resp.text)

        if not resp.ok:
            raise LibraryNotFoundError(resp.url)

        return parse_infos(q)

    @auth_required
    def borrowed(self, verbose=False):
        '''获取用户已借书籍信息列表

        书籍信息包括：

        - 书籍名字 name
        - 书籍控制号 ctrlno
        - 作者 author
        - 借出日期 borrowed_date
        - 最迟归还日期 deadline
        - 是否可以续借 renewable
        - 详细书籍信息 details （如果 `verbose` 为真）

        如果没有找到任何记录，返回空列表

        :param verbose: 是否返回详细的书籍信息
        '''
        def parse_records(pq):
            pattern = re.compile(u'.*ctrlno=(\d+).*>(.*)／(.*)<')
            _ = _convert_datetime

            records = []
            for record in pq('#borrowedcontent tbody tr'):
                td = PQ('td', record)
                ctrlno, name, author = pattern.findall(PQ(td[2]).html())[0]
                records.append({
                    'name': name,
                    'ctrlno': ctrlno,
                    'author': author,
                    'borrowed_date': _(PQ(td[6]).text().strip()),
                    'deadline': _(PQ(td[1]).text().strip()),
                    'renewable': not (PQ(td[0]).text().strip() == u'续满')
                })
            return records

        dest = self._build_url('/user/bookborrowed.aspx')

        resp = requests.get(dest, cookies=self.cookies)
        q = PQ(resp.text)

        if not resp.ok:
            raise LibraryNetworkError(resp.url)

        records = parse_records(q)

        if verbose:
            records = self._get_details(records)

        return records

    @auth_required
    def requested(self, verbose=False):
        '''获取用户预约书籍信息列表

        书籍信息包括：

        - 书籍名字 name
        - 书籍控制号 ctrlno
        - 作者 author
        - 预约日期 requested_date
        - 最迟借阅日期 deadline
        - 是否可取 accessable
        - 取书地点 access_location
        - 详细书籍信息 details （如果 `verbose` 为真）

        如果没有找到任何记录，返回空列表

        :param verbose: 是否返回详细的书籍信息
        '''
        def parse_records(pq):
            pattern = re.compile(u'.*ctrlno=(\d+).*>(.*)／(.*)<')
            _ = _convert_datetime

            records = []
            for record in pq('table tbody tr'):
                td = PQ('td', record)
                ctrlno, name, author = pattern.findall(PQ(td[2]).html())[0]
                deadline = PQ(td[1]).text().strip() or None
                records.append({
                    'name': name,
                    'ctrlno': ctrlno,
                    'author': author,
                    'requested_date': _(PQ(td[6]).text().strip()),
                    'deadline': _(deadline) if deadline else None,
                    'accessable': deadline is not None,
                    'access_location': PQ(td[7]).text().strip()
                })
            return records

        dest = self._build_url('/user/resvp.aspx')

        resp = requests.get(dest, cookies=self.cookies)
        q = PQ(resp.text)

        if not resp.ok:
            raise LibraryNetworkError

        records = parse_records(q)

        if verbose:
            records = self._get_details(records)

        return records

    @auth_required
    def history(self, verbose=False):
        '''获取用户借书历史记录

        书籍信息包括：

        - 书籍名字 name
        - 书籍控制号 ctrlno
        - 作者 author
        - 借出日期 borrowed_date
        - 归还日期 returned_date
        - 详细书籍信息 details （如果 `verbose` 为真）

        如果没有找到任何记录，返回空列表

        :param verbose: 是否返回详细的书籍信息
        '''
        def parse_records(pq):
            current_page = int(pq('#ctl00_cpRight_Pagination2_dplbl2').text())
            total_page = int(pq('#ctl00_cpRight_Pagination2_gplbl2').text())

            pattern = re.compile(u'.*ctrlno=(\d+).*>(.*)／(.*)<')
            _ = _convert_datetime

            records = []
            for record in pq('table tbody tr'):
                td = PQ('td', record)
                ctrlno, name, author = pattern.findall(PQ(td[2]).html())[0]
                records.append({
                    'name': name,
                    'ctrlno': ctrlno,
                    'author': author,
                    'borrowed_date': _(PQ(td[0]).text().strip()),
                    'returned_date': _(PQ(td[1]).text().strip())
                })
            return records, current_page < total_page

        dest, page = self._build_url('user/bookborrowedhistory.aspx'), 1

        records = []
        while True:
            resp = requests.get(dest, params={'page': page},
                                cookies=self.cookies)
            q = PQ(resp.text)

            if not resp.ok:
                raise LibraryNetworkError

            record, has_next = parse_records(q)
            records = records + record

            if not has_next:
                break
            page = page + 1

        if verbose:
            records = self._get_details(records)

        return records

    @auth_required
    def recommended(self):
        '''获取用户推荐购买书籍记录

        书籍信息包括：

        - 书籍名称 name
        - 书籍是否购买 purchased

        如果没有找到任何记录，返回空列表
        '''
        def parse_records(pq):
            current_page = int(pq('#ctl00_cpRight_Pagination2_dplbl2').text())
            total_page = int(pq('#ctl00_cpRight_Pagination2_gplbl2').text())

            records = []
            for record in pq('table tbody tr'):
                td = PQ('td', record)
                records.append({
                    'name': PQ(td[0]).text().strip(),
                    'purchased': PQ(td[4]).text().strip() == u'已订购'
                })
            return records, current_page < total_page

        dest, page = self._build_url('user/myrecommendlist.aspx'), 1

        records = []
        while True:
            resp = requests.get(dest, params={'page': page},
                                cookies=self.cookies)
            q = PQ(resp.text)

            if not resp.ok:
                raise LibraryNetworkError

            record, has_next = parse_records(q)
            records = records + record

            if not has_next:
                break
            page = page + 1

        return records
