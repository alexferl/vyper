from setuptools import setup

setup(
    name='vyper',
    version='0.0.1',
    description='Python configuration with fangs',
    url='http://github.com/admiralobvious/vyper',
    author='Alexandre Ferland',
    author_email='aferlandqc@gmail.com',
    license='MIT',
    packages=['vyper'],
    zip_safe=False,
    install_requires=[
        'future',
        'pathlib',
        'pytoml',
        'PyYAML'
    ],
    tests_require=[
        'nose'
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
