#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# Copyright (C) 2005-2007 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://bitten.edgewall.org/wiki/License.

import os
import sys
from setuptools import setup, find_packages, Feature
from setuptools.command import egg_info

sys.path.append(os.path.join('doc', 'common'))
try:
    from doctools import build_doc, test_doc
except ImportError:
    build_doc = test_doc = None

# Turn off multiprocessing logging
# Bug in setuptools/distutils test runner using Python 2.6.2+?
import logging
if hasattr(logging, 'logMultiprocessing'):
    logging.logMultiprocessing = 0

NS_old = 'http://bitten.cmlenz.net/tools/'
NS_new = 'http://bitten.edgewall.org/tools/'
tools = [
        'sh#exec = iTest.build.shtools:exec_',
        'sh#pipe = iTest.build.shtools:pipe',
        'c#configure = iTest.build.ctools:configure',
        'c#autoreconf = iTest.build.ctools:autoreconf',
        'c#cppunit = iTest.build.ctools:cppunit',
        'c#cunit = iTest.build.ctools:cunit',
        'c#gcov = iTest.build.ctools:gcov',
        'c#make = iTest.build.ctools:make',
        'mono#nunit = iTest.build.monotools:nunit',
        'java#ant = iTest.build.javatools:ant',
        'java#junit = iTest.build.javatools:junit',
        'java#cobertura = iTest.build.javatools:cobertura',
        'php#phing = iTest.build.phptools:phing',
        'php#phpunit = iTest.build.phptools:phpunit',
        'php#coverage = iTest.build.phptools:coverage',
        'python#coverage = iTest.build.pythontools:coverage',
        'python#distutils = iTest.build.pythontools:distutils',
        'python#exec = iTest.build.pythontools:exec_',
        'python#figleaf = iTest.build.pythontools:figleaf',
        'python#pylint = iTest.build.pythontools:pylint',
        'python#trace = iTest.build.pythontools:trace',
        'python#unittest = iTest.build.pythontools:unittest',
        'svn#checkout = iTest.build.svntools:checkout',
        'svn#export = iTest.build.svntools:export',
        'svn#update = iTest.build.svntools:update',
        'hg#pull = iTest.build.hgtools:pull',
        'xml#transform = iTest.build.xmltools:transform'
    ]
recipe_commands = [NS_old + tool for tool in tools] \
                  + [NS_new + tool for tool in tools]

class MasterFeature(Feature):

    def exclude_from(self, dist):
        # Called when master is disabled (--without-master)
        pass

    def include_in(self, dist):
        # Called when master is enabled (default, or --with-master)
        dist.metadata.name = 'iTest'
        dist.metadata.description = 'Continuous integration for Spreadtrum'
        dist.long_description = "A Trac plugin for collecting software " \
                                "metrics via continuous integration."""
        # Use full manifest when master is included
        egg_info.manifest_maker.template = "MANIFEST.in"
        # Include tests in source distribution
        if 'sdist' in dist.commands:
            dist.packages = find_packages()
        else:
            dist.packages = find_packages(exclude=['*tests*'])
        dist.test_suite = 'iTest.tests.suite'
        dist.package_data = {
              'iTest': ['htdocs/*.*',
                    'htdocs/charts_library/*.swf',
                    'templates/*.html',
                    'templates/*.txt']}
        dist.entry_points['trac.plugins'] = [
                    'iTest.admin = iTest.admin',
                    'iTest.main = iTest.main',
                    #'iTest.master = iTest.master',
                    'iTest.web_ui = iTest.web_ui'
                    #'iTest.testing = iTest.report.testing',
                    #'iTest.coverage = iTest.report.coverage',
                    #'iTest.lint = iTest.report.lint',
                    #'iTest.notify = iTest.notify'
                    ]

master = MasterFeature(
    description = "Bitten Master Trac plugin",
    standard = True,
    py_modules = [])


if os.path.exists(os.path.join(os.path.dirname(__file__), 'MANIFEST.in')):
    available_features = {"master": master}

setup(
    name = 'iTest',
    version =  '1.0',
    author = 'Song.Shan',
    author_email = '',
    license = 'SPRD',
    url = '',
    download_url = '',
    zip_safe = False,
    description = '',
    long_description = "" ,
    
    packages = {},
    py_modules = [],
    test_suite = '',
    tests_require = [
        'figleaf',
    ],
    entry_points = {
        'console_scripts': [],
        'distutils.commands': [],
        'iTest.recipe_commands': ''
    },    
    features = available_features,
    cmdclass = {'build_doc': build_doc, 'test_doc': test_doc}
)
