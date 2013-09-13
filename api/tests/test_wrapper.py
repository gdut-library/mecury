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

    def testLogin(self):
        library = LibraryAuthWrapper()

        self.assertTrue('sulcmiswebpac' in library.login(USERNAME, PASSWORD))
        self.assertRaises(LibraryLoginError, library.login, USERNAME, '12345')
        self.assertRaises(LibraryChangePasswordError, library.login,
                          UNACTIVATE_USERNAME, UNACTIVATE_PASSWORD)

        token = library.login(USERNAME, PASSWORD)['sulcmiswebpac']
        self.assertTrue(library.check_login(token))
        self.assertFalse(library.check_login('12345'))


if __name__ == '__main__':
    unittest.main()
