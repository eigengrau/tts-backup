#!/usr/bin/env python

import subprocess
import shlex
from setuptools import setup


try:
    revision = (
        subprocess
        .check_output(shlex.split('git rev-parse --short HEAD'))
        .rstrip()
        .decode('ASCII')
    )
except:
    revision = '0.1.0.0'


setup(
    name='tts-backup',
    version=revision,
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
    package_dir={
        'tts_tools': 'src',
        'tts_tools.libgui': 'src/libgui',
        'tts_tools.backup': 'src/backup',
        'tts_tools.prefetch': 'src/prefetch'
    },
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
