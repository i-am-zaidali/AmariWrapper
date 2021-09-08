from setuptools import setup

setup(
    name='amari',
    version='1.2.1',    
    description='An asynchronous AmariBot API wrapper.',
    url='git@github.com:i-am-zaidali/AmariWrapper.git',
    author='Zaid Ali',
    author_email='zaidlastid20@gmail.com',
    install_requires=['aiohttp', 'cachetools', 'requests']
)