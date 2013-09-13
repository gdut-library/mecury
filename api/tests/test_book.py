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
        books_info = self.book.search(u'深入理解计算机系统', verbose=True)

        self.assertEqual(len(books_info), 3)
        self.assertEqual(books_info[0]['ctrlno'], '574811')
        self.assertEqual(books_info[1]['total'], 4)
        self.assertEqual(books_info[2]['available'], 3)
        self.assertEqual(books_info[0]['details'], self.book.get('574811'))

        self.assertRaises(LibraryNotFoundError, self.book.search,
                          'gdut library wrapper')
