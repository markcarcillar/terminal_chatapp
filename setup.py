from setuptools import setup

with open('README.md') as readmefile:
    long_description = readmefile.read()

setup(
    name='terminal-chatapp',
    version='1.0.2',
    author='Mark Carcillar',
    description='Secure communication on terminal.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/clediscover/terminal_chatapp',
    packages=['terminal_chatapp'],
    install_requires = [
        'websockets',
        'cryptography'
    ],
    python_requires='>=3.6'
)