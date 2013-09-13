#coding: utf-8

import re
from setuptools import setup
from email.utils import parseaddr


declaration = open('api/__init__.py').read()


def grep(item):
    pattern = re.compile('__%s__ = \'(.*)\'' % item)
    return pattern.findall(declaration)[0]

author, author_email = parseaddr(grep('author'))


setup(
    name='GDUT Library API',
    version=grep('version'),
    author=author,
    author_email=author_email,
    url=grep('homepage'),
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
