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
        'PyYAML',
        'toml'
    ]
)
