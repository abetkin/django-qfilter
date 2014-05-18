from setuptools import setup, find_packages
import codecs
import os
import re

import qfilters

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="qfilters",

    # There are various approaches to referencing the version. For a discussion,
    # see http://packaging.python.org/en/latest/tutorial.html#version
    version=qfilters.__version__,

    description="Filters for django",
    long_description=long_description,

    # The project URL.
    url='https://github.com/abetkin/django-qfilter',

    # Author details
    author='abetkin',
    author_email='abvit89@gmail.com',

    # Choose your license
    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='django filters',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages.
    packages=["qfilters"],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed.
    install_requires = ['django'],

    # TODO! ipython script
    #entry_points={
        #'console_scripts': [
            #'qfilters_test=tests:main',
        #],
    #},
)
