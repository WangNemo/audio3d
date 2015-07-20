﻿# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name = "3DAudio",
    version = "1.0",
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '3daudio': ['*.png','*.wav'],
    },
    install_requires = ['pyopengl','pyaudio','pyside'],
    entry_points={
        'console_scripts': [
            '3daudio = 3daudio.main:main',
        ],
    }

)
