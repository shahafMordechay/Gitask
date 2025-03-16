from setuptools import setup, find_packages

setup(
    name='gitask',
    version='1.0.1',
    description="A CLI tool to streamline your workflow by integrating with your PMT and VCS.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Shahaf Mordechay",
    url="https://github.com/shahafMordechay/Gitask",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',            # Click library for CLI handling
        'jira',             # Jira Python client
        'requests',         # Requests library for HTTP requests
        'python-gitlab',    # Gitlab Python client
    ],
    entry_points={
        'console_scripts': [
            'gitask = gitask.main:cli',  # Main entry point for the `gitask` command
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
