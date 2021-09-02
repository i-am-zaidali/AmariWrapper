from setuptools import setup

setup(
    name='amari',
    version='1.1.0',    
    description='An asynchronous AmariBot API wrapper.',
    url='https://github.com/i-am-zaidali/AmariWrapper',
    author='Zaid Ali',
    author_email='zaidlastid20@gmail.com',
    packages=['amari'],
    install_requires=['aiohttp']
)