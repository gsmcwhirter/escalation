#!/usr/bin/env python

from setuptools import setup

setup (
    name = 'gametheory.escalation',
    version = '0.1',
    packages = [
        "gametheory.escalation"
    ],
    package_dir = {
        '': 'src',
    },
    install_requires = [
        'distribute',
        'gametheory.base'
    ],
    dependency_links = ["https://www.ideafreemonoid.org/pip"],
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
