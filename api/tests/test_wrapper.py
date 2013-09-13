#coding: utf-8

import unittest

from api.library import (
    LibraryAuthWrapper,
    LibraryLoginError,
    LibraryChangePasswordError
)
from config import (
    USERNAME, PASSWORD,
    UNACTIVATE_USERNAME, UNACTIVATE_PASSWORD
)


class WrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.library = LibraryAuthWrapper()

    def testLogin(self):
        self.assertTrue('sulcmiswebpac' in
                        self.library.login(USERNAME, PASSWORD))
        self.assertRaises(LibraryLoginError, self.library.login,
                          USERNAME, '12345')
        self.assertRaises(LibraryChangePasswordError, self.library.login,
                          UNACTIVATE_USERNAME, UNACTIVATE_PASSWORD)

    def testCheckLogin(self):

        token = self.library.login(USERNAME, PASSWORD)['sulcmiswebpac']
        self.assertTrue(self.library.check_login(token))
        self.assertFalse(self.library.check_login('12345'))
