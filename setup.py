#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name='flightgear-rx',
    version='0.1.0',
    packages=find_packages(),
    
    install_requires=['rx'],

    test_suite='tests',

    author='Eduard Bopp',
    description='Reactive remote API to FlightGear simulator',
    url='https://github.com/aepsil0n/flightgear-python-rx',
)
