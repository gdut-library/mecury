#coding: utf-8

from setuptools import setup

import api
from email.utils import parseaddr
author, author_email = parseaddr(api.__author__)

setup(
    name='GDUT Library API',
    version=api.__version__,
    author=author,
    author_email=author_email,
    url=api.__homepage__,
    description='Provide a programmable API for GDUT library.',
    long_description=open('README.mkd').read(),
    license='BSD',
    packages=['api', 'api.tests'],
    install_requires=[
        'pyquery>=1.2.4',
        'requests>=1.2.3',
        'nose>=1.3.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: OSI Approved :: BSD License'
    ]
)
