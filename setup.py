# ~*~ coding: utf-8 ~*~
from setuptools import setup, find_packages
import re


requirements = open('./requirements.txt', 'r')
requirements_dev = open('./requirements-dev.txt', 'r')

with open('./pullpreview/__init__.py', 'r') as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)

setup(
    name='pullpreview',
    version=version,
    author='Mark Story',
    author_email='mark@sentry.io',
    url='https://github.com/getsentry/pull-preview/',
    description='''An application that proxies requests to sentry.io 
    and allows pull requests to be previewed before merging.
    ''',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=find_packages(),
    install_requires=requirements.readlines(),
    include_package_data=True,
    zip_safe=False,
    entry_points={},
    classifiers=[
        'Framework :: Flask',
    ],
    tests_require=requirements_dev.readlines()
)
