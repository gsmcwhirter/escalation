#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='escalation',
    version='0.3.1',
    packages=[
        "escalation"
    ],
    install_requires=[
        'simulations>=0.5.0'
    ],
    package_dir={
        '': 'src',
    },
    dependency_links=["https://www.ideafreemonoid.org/pip"],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'simulations>=0.5.0'
    ],
    author='Gregory McWhirter',
    author_email='gmcwhirt@uci.edu',
    description='Game theory simulations for escalation research',
    url='https://www.github.com/gsmcwhirter/escalation',
    license='MIT',
    scripts=[
        "scripts/escalation.sim.py",
        "scripts/escalation.stats.py"
    ]
)
