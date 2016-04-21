#!/usr/bin/env python

import subprocess
import shlex
from setuptools import setup


version = '0.1.0.1'

try:
    hash = (
        subprocess
        .check_output(shlex.split('git rev-parse --short HEAD'))
        .rstrip()
        .decode('ASCII')
    )
    commit = (
        subprocess
        .check_output(shlex.split('git rev-list --count HEAD'))
        .rstrip()
        .decode('ASCII')
    )
except:
    pass
else:
    version = '{}.dev{}+{}'.format(version, commit, hash)


setup(
    name='tts-backup',
    version=version,
    description=(
        "Backup Tabletop Simulator saves and assets into comprehensive "
        "Zip files."
    ),
    author="Sebastian Reuße",
    author_email='seb@wirrsal.net',
    url='https://github.com/eigengrau/tts-backup',
    packages=[
        'tts_tools',
        'tts_tools.backup',
        'tts_tools.prefetch',
        'tts_tools.libgui'
    ],
    package_dir={'': 'src'},
    license="GPL3",
    entry_points={
        'console_scripts': [
            'tts-backup = tts_tools.backup.cli:console_entry',
            'tts-prefetch = tts_tools.prefetch.cli:console_entry'
        ],
        'gui_scripts': [
            'tts-backup-gui = tts_tools.backup.gui:gui_entry',
            'tts-prefetch-gui = tts_tools.prefetch.gui:gui_entry'
        ]
    }
)
