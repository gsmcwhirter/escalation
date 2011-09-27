__author__="gmcwhirt"
__date__ ="$Sep 26, 2011 2:43:53 PM$"

from setuptools import setup, find_packages

setup (
  name = 'gametheory.escalation',
  version = '0.0.1',
  packages = find_packages('src'),
  package_dir = {
    '': 'src',
  },
  namespace_packages = ['gametheory'],
  author = 'Gregory McWhirter',
  author_email = 'gmcwhirt@uci.edu',
  description = 'Game theory simulations for escalation research',
  url = 'https://www.github.com/gsmcwhirter/gametheory',
  license = 'MIT',
  entry_points = {
    "console_scripts": [
        "gt.escalation.sim = gametheory.escalation.simulations:run",
        "gt.escalation.stats = gametheory.escalation.stats:run"
    ]
  }
)
