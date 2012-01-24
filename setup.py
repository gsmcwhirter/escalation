#!/usr/bin/env python

from setuptools import setup

setup (
    name = 'gametheory.escalation',
    version = '0.2.2',
    packages = [
        "gametheory.escalation"
    ],
    package_dir = {
        '': 'src',
    },
    install_requires = [
        'distribute',
        'gametheory.base >= 0.3.6'
    ],
    dependency_links = ["https://www.ideafreemonoid.org/pip"],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    author = 'Gregory McWhirter',
    author_email = 'gmcwhirt@uci.edu',
    description = 'Game theory simulations for escalation research',
    url = 'https://www.github.com/gsmcwhirter/gametheory',
    license = 'MIT',
    scripts = [
        "scripts/gt.escalation.sim",
        "scripts/gt.escalation.stats"
    ]
)
