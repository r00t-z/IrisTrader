# setup.py

from setuptools import find_packages, setup

# Read the contents of the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='iris-mt5-bridge', 
    packages=find_packages(),
    version='1.0.0',
    description='A clean, modern bridge to connect Python on Linux to MetaTrader 5 on Wine.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='r00tz',
    license='MIT',
    # url = 'YOUR GITHUB REPO URL HERE', # You can add this later
    install_requires=requirements, # Reads dependencies from requirements.txt
    entry_points={
        'console_scripts': [
            'iris-server=irismt5linux.__main__:main',
        ],
    },
    python_requires='>=3.8',
)