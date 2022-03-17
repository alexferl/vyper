from setuptools import setup

setup(
    name="vyper-config",
    version="1.1.0",
    description="Python configuration with (more) fangs",
    url="http://github.com/alexferl/vyper",
    author="Alexandre Ferland",
    author_email="me@alexferl.com",
    license="MIT",
    packages=["vyper"],
    zip_safe=False,
    install_requires=[
        "distconfig3>=1.0.1",
        "toml>=0.10.0",
        "PyYAML>=5.4.1",
        "watchdog>=0.10.0",
    ],
    setup_requires=["pytest-runner>=6.0.0"],
    tests_require=["pytest>=7.1.0"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
