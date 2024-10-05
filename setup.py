from setuptools import setup, find_packages

setup(
    name='gitask',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',   # Click library for CLI handling
        'jira',    # Jira Python client
    ],
    entry_points={
        'console_scripts': [
            'gitask = gitask.main:cli',  # Main entry point for the `gitask` command
        ],
    },
)
