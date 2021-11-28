from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
VERSION_FILE = path.join(here, 'VERSION')


def get_version():
    with open(VERSION_FILE) as f:
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            return line
        raise AttributeError("Package does not have a __version__")


def get_long_description():
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name='apipyfy',
    version=get_version(),
    description='Python scripts to provide "API" interface for website that does not provide one ',
    long_description=get_long_description(),
    url='https://github.com/jychp/apipyfy',
    author='Jychp',
    author_email='jeremy.chapeau@protonmail.com',
    license="None",
    classifiers=[
        'Programming Language :: Python :: 3.8'
    ],
    keywords='python package template',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    setup_requires=['pytest-runner', 'setuptools>=38.6.0'],
    install_requires=['bs4', 'pyduktape', 'requests'],
    tests_require=['pytest', 'pytest-cov']
)