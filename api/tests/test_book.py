#coding: utf-8

import unittest

from api.book import Book, LibraryNotFoundError


class BookTestCase(unittest.TestCase):

    def setUp(self):
        self.book = Book()

    def testGet(self):
        book_info = self.book.get(574811)

        self.assertEqual(book_info['name'], u'Computer systems[monograph]'
                         u'＝深入理解计算机系统 ：a programmer\'s'
                         u' perspective ：Second edition')
        self.assertEqual(book_info['isbn'], '9787111326311')
        self.assertEqual(book_info['ctrlno'], '574811')
        self.assertEqual(len(book_info['locations']), 2)

        self.assertRaises(LibraryNotFoundError, self.book.get, 'not_a_book')

    def testSearch(self):
        books_info = self.book.search(u'计算机', verbose=True, limit=13)

        self.assertEqual(len(books_info), 13)

        self.assertRaises(LibraryNotFoundError, self.book.search,
                          'gdut library wrapper')

    def testSearchUnicode(self):
        self.assertRaises(LibraryNotFoundError, self.book.search,
                          u'ノ・ゾ・キ・ア・ナ')
