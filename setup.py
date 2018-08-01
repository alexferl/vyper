from setuptools import setup

# Original repository: http://github.com/admiralobvious/vyper implemented by Alexandre Ferland
# Changed the author_email and url to make it point to the forked repo.
# I kept the original author_email and url as original_url and original_author_email

setup(
    name='vyper',
    version='0.1.0',
    description='Python configuration with more fangs',
    original_url='http://github.com/admiralobvious/vyper',
    url='http://github.com/benjaminch/vyper',
    author='Alexandre Ferland',
    original_author_email='aferlandqc@gmail.com',
    author_email='benjamin.chastanier@gmail.com',
    license='MIT',
    packages=['vyper'],
    zip_safe=False,
    install_requires=[
        'distconfig>=0.1',
        'future>=0.15',
        'pathlib>=1.0',
        'pytoml>=0.1',
        'PyYAML>=3.11',
        'watchdog>=0.8'
    ],
    tests_require=[
        'nose>=1.3'
    ],
    test_suite='nose.collector',
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
