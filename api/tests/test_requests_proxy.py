#coding: utf-8

import unittest

from api.utils import requests
from api.library import LibraryNetworkError


class RequestsProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.valid_uri = 'http://127.0.0.1'
        self.invalid_uri = 'http://somewhere'

    def testGet(self):
        normal_resp = requests.get(self.valid_uri)
        self.assertEqual(normal_resp.status_code, 200)

        self.assertRaises(LibraryNetworkError, requests.get, self.invalid_uri)
