# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Yandex Player',
    version='0.1.0',
    description='A little program to find and download music from Yandex Music',
    long_description=readme,
    author='Egor Panasenko',
    author_email='gaura.panasenko@gmail.com',
    url='https://github.com/gaurapanasenko/yandex-player',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)