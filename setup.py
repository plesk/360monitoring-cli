#!/usr/bin/env python3

import os
import sys
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.md')).read()
install_requires = ['configparser', 'prettytable', 'requests']

setuptools.setup(
    name='360monitoringcli',
    version='1.0.17',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Monitoring',
    ],
    keywords='360 system monitoring cli',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            '360monitoring=cli360monitoring.monitoring:main',
        ],
    },
    data_files=[('share/doc/360monitoring-cli', [
        '360monitoring-example.ini',
        'LICENSE',
        'README.md',
    ])],
    python_requires='>=3.0'
)
