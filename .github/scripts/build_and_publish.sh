#!/bin/bash

# Build the package
poetry build

# Publish to PyPI
poetry publish --username __token__ --password $PYPI_API_TOKEN --no-interaction 
