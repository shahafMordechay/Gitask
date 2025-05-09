#!/bin/bash

# Build the package
poetry build

# Publish to PyPI
if [ "$TEST_MODE" = "true" ]; then
    echo "TEST MODE: Would publish to PyPI"
    poetry publish --dry-run
else
    poetry publish --username __token__ --password $PYPI_API_TOKEN --no-interaction
fi 
