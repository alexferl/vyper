from setuptools import setup

setup(
    name="vyper-config",
    version="1.0.0",
    description="Python configuration with (more) fangs",
    url="http://github.com/alexferl/vyper",
    author="Alexandre Ferland",
    author_email="aferlandqc@gmail.com",
    license="MIT",
    packages=["vyper"],
    zip_safe=False,
    install_requires=[
        "distconfig3>=1.0.1",
        "toml>=0.10.0",
        "PyYAML>=5.3.1",
        "watchdog>=0.10.0",
    ],
    # setup_requires=["pytest-runner>=5.2"],
    tests_require=["pytest>=6.1.2"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
