from setuptools import setup

setup(
    name='vyper-config',
    version='0.2.3',
    description='Python configuration with more fangs',
    url='http://github.com/admiralobvious/vyper',
    author='Alexandre Ferland',
    author_email='aferlandqc@gmail.com',
    license='MIT',
    packages=['vyper'],
    zip_safe=False,
    install_requires=[
        'distconfig>=0.1.0',
        'future>=0.16.0',
        'pathlib>=1.0.1',
        'pytoml>=0.1.18',
        'PyYAML>=3.13',
        'watchdog>=0.8.3'
    ],
    tests_require=[
        'nose2>=0.8.0'
    ],
    test_suite='nose2.collector.collector',
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
