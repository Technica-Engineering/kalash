from setuptools import setup, find_packages
from collections import defaultdict
import os
import sys
import subprocess

interpreter_path = sys.executable

# preinstall pyyaml before it's imported in the setup
subprocess.call([interpreter_path, "-m", "pip", "install", "pyyaml"])

import yaml

with open(os.path.join(os.path.dirname(__file__), 'meta.yaml')) as f:
    meta = yaml.full_load(f)

with open("README.md", "r") as f:
    readme = f.read()

SETUP_DEPENDENCIES = ['setuptools', 'wheel']
KALASH_REQUIRES = [
    'thesmuggler', 
    'pyyaml', 
    'argparse', 
    'unittest-xml-reporting', 
    'parameterized',
    'pylint',
    'toolz'
]

LINTER_RELATIVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'kalash_lint')

setup(
    name='kalash',
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['kalash=kalash.run:main_cli']
    },
    extras_require={
        "dev": [
            'pdoc3',
            'flake8',
            'twine',
            'setuptools'
        ]
    },
    setup_requires=SETUP_DEPENDENCIES,
    install_requires=KALASH_REQUIRES,
    version=meta['version'],
    description=meta['kalash']['description'],
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=meta['keywords'],
    author=meta['author'],
    author_email=meta['email'],
    license=meta['license'],
    packages=find_packages(),
    package_data={'': ['spec.yaml']},
    include_package_data=True,
    zip_safe=False
)