from setuptools import setup

setup(
    name="vyper-config",
    version="0.5.0",
    description="Python configuration with (more) fangs",
    url="http://github.com/admiralobvious/vyper",
    author="Alexandre Ferland",
    author_email="aferlandqc@gmail.com",
    license="MIT",
    packages=["vyper"],
    zip_safe=False,
    install_requires=[
        "distconfig>=0.1.0",
        "pathlib>=1.0.1",
        "pytoml>=0.1.20",
        "PyYAML>=5.1",
        "watchdog>=0.9.0",
    ],
    setup_requires=["pytest-runner>=5.1"],
    tests_require=["pytest>=5.0.1"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
