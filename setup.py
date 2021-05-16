from setuptools import setup

setup(
    name='terminal-chatapp',
    version='1.0.0',
    packages=['terminal_chatapp'],
    install_requires = [
        'websockets',
        'cryptography'
    ]
)