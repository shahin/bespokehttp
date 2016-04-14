from setuptools import setup, find_packages

exec(open('bespokehttp/version.py').read())

setup(
    name='bespokehttp',
    version=__version__,
    description='A simple HTTP server for serving static files.',
    author='Shahin',
    license='MIT',

    packages=find_packages(),
    install_requires=[],
)
