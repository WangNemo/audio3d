from setuptools import setup, find_packages
setup(
    name = "3DAudio",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '3daudio': ['*.png','*.wav','*.jpg'],
    },
    install_requires = ['pyopengl','pyaudio','python-qt'],
    entry_points={
        'console_scripts': [
            '3daudio = 3daudio.main:main',
        ],
    }

)
