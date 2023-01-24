#!/usr/bin/env python3

import os
import sys
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.md')).read()
install_requires = ['argparse', 'configparser', 'prettytable', 'requests']

setuptools.setup(
    name='360monitoring-cli',
    version='1.0.1',
    description='360 Monitoring CLI',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/plesk/360monitoring-cli',
    author='Jan Loeffler',
    author_email='jan.loeffler@webpros.com',
    maintainer='Jan Loeffler',
    maintainer_email='jan.loeffler@webpros.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
    ],
    keywords='360 system monitoring cli',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            '360monitoring=360monitoring-cli.360monitoring:main',
        ],
    },
    data_files=[('share/doc/360monitoring-cli', [
        '360monitoring-example.ini',
        'LICENSE',
        'README.md',
    ])],
)
