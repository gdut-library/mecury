#coding: utf-8

import re
import requests
from pyquery import PyQuery as PQ

from .library import LibraryWrapper, LibraryNotFoundError, LibraryNetworkError

__all__ = ['Book']


class Book(LibraryWrapper):
    '''馆藏信息接口'''

    def get(self, ctrlno):
        '''根据 ctrlno 获取书籍信息

        书籍信息包括：

        - 书籍名称 name
        - 书籍 ISBN 码 isbn
        - 书籍系统控制号 ctrlno
        - 书籍馆藏信息 locations

        如果书籍没有找到，抛出 `LibraryNotFoundError`

        :param ctrlno: 书籍在图书馆内的系统控制号
        '''

        def parse_name(pq):
            raw = pq('#ctl00_ContentPlaceHolder1_bookcardinfolbl').text()
            match = re.compile(u'(.*)[＝]?.*／').findall(raw)
            if match:
                return match[0]

        def parse_isbn(pq):
            raw = pq('#ctl00_ContentPlaceHolder1_bookcardinfolbl').text()
            match = re.compile(u'[ISBN]?([978|7]+\-[\d-]+).*').findall(raw)
            if match:
                return match[0].replace('-', '')

        def parse_ctrlno(pq):
            return str(ctrlno)

        def parse_locations(pq):
            locations = []
            for tr in pq('#bardiv tbody tr'):
                td = PQ(tr)('td')
                locations.append({
                    'library': PQ(td[0]).text().strip(),
                    'location': PQ(td[1]).text().strip(),
                    'status': PQ(td[5]).text().strip()
                })
            return locations

        dest = self._build_url('/bookinfo.aspx')
        params = {'ctrlno': ctrlno}

        resp = requests.get(dest, params=params)
        q = PQ(resp.text)

        if not resp.ok or len(q('#searchnotfound')):
            raise LibraryNotFoundError

        #: FIXME pyquery 有时候不能选择到 `#searchnotfound`
        #:       这个元素
        try:
            return {
                'name': parse_name(q),
                'isbn': parse_isbn(q),
                'ctrlno': parse_ctrlno(q),
                'locations': parse_locations(q)
            }
        except TypeError:
            raise LibraryNotFoundError

    def search(self, q, verbose=False, limit=0):
        '''搜索图书馆，返回搜索列表。

        搜索列表每个项目包含：

        - 书籍名字 name
        - 书籍控制号 ctrlno
        - 作者 author
        - 出版社 publisher
        - 馆藏位置 location
        - 馆藏数量 total
        - 馆藏剩余量 available
        - 详细书籍信息 details （如果 `verbose` 为真）

        如果没有找到任何搜索结果，抛出 `LibraryNotFoundError`

        :param q: 查询关键字
        :param verbose: 是否返回详细的书籍信息
        :param limit: 限制返回长度, 0 为不限制
        '''

        def parse_results(pq):
            current_page = int(pq(
                '#ctl00_ContentPlaceHolder1_dplblfl2').text())
            total_page = int(pq('#ctl00_ContentPlaceHolder1_gplblfl2').text())

            results = []
            for tr in pq('table tbody tr'):
                td = PQ(tr)('td')
                results.append({
                    'name': PQ(td[1]).text().strip(),
                    'ctrlno': PQ('input', td[0]).attr('value'),
                    'author': PQ(td[2]).text().strip(),
                    'publisher': PQ(td[3]).text().strip(),
                    'location': PQ(td[5]).text().strip(),
                    'total': int(PQ(td[6]).text().strip()),
                    'available': int(PQ(td[7]).text().strip())
                })
            return results, current_page < total_page

        dest = self._build_url('/searchresult.aspx')

        # 查询关键字编码要为 gb2312
        params = {
            'anywords': q.encode('gbk'),
            'page': 1,
            # 单页显示数目
            'dp': 50
        }

        records = []
        while True:
            resp = requests.get(dest, params=params)
            q = PQ(resp.text)

            if not resp.ok:
                raise LibraryNetworkError
            if len(q('.msg')):
                raise LibraryNotFoundError

            record, has_next = parse_results(q)
            records = records + record

            if not has_next or (len(records) >= limit and limit > 0):
                break
            params['page'] = params['page'] + 1

        if not len(records):
            raise LibraryNotFoundError

        if limit != 0:
            records = records[0:limit]

        if verbose:
            for i in records:
                i['details'] = self.get(i['ctrlno'])

        return records
