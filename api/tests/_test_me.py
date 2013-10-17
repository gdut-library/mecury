#coding: utf-8

import unittest

from api.me import Me, LibraryLoginRequired
from api.book import Book

from config import USERNAME, PASSWORD, USERINFOS, BOOKINFOS


class MeTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Me()
        self.token = self.client.login(USERNAME, PASSWORD)['sulcmiswebpac']

    def testPersonal(self):
        self.assertRaises(LibraryLoginRequired, self.client.personal,
                          'invalid_token')
        self.assertEqual(USERINFOS, self.client.personal(self.token))

    def testBorrowed(self):
        self.assertRaises(LibraryLoginRequired, self.client.borrowed,
                          'invalid_token')

        borrowed = self.client.borrowed(self.token, True)
        self.assertEqual(BOOKINFOS['borrowed'], len(borrowed))
        self.assertEqual(BOOKINFOS['renewable'],
                         len(filter(lambda x: x['renewable'], borrowed)))
        self.assertEqual(borrowed[0]['details'],
                         Book().get(borrowed[0]['ctrlno']))

    def testRequested(self):
        self.assertRaises(LibraryLoginRequired, self.client.requested,
                          'invalid_token')

        requested = self.client.requested(self.token, True)
        self.assertEqual(BOOKINFOS['requested'], len(requested))
        self.assertEqual(requested[0]['details'],
                         Book().get(requested[0]['ctrlno']))

    def testHistory(self):
        self.assertRaises(LibraryLoginRequired, self.client.history,
                          'invalid_token')

        history = self.client.history(self.token, True)
        self.assertEqual(BOOKINFOS['total_borrowed'], len(history))
        self.assertEqual(history[0]['details'],
                         Book().get(history[0]['ctrlno']))

    def testRecommended(self):
        self.assertRaises(LibraryLoginRequired, self.client.recommended,
                          'invalid_token')

        recommended = self.client.recommended(self.token)
        self.assertEqual(BOOKINFOS['total_recommened'], len(recommended))
