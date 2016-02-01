from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
setup(
    name='minipoker',
    version='0.0.2',
    description='Poker Game',
    long_description='Simple implementation for a poker game',
    url='https://github.com/reutsharabani/minipoker',
    # Author details
    author='Reut Sharabani',
    author_email='reut.sharabani@gmail.com',
    # Choose your license
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment :: Board Games',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    # What does your project relate to?
    keywords='poker game',
    # You can just specify the packages manually here if your project is
    #  simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['']
)