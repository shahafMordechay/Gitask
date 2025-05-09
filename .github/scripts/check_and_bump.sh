#!/bin/bash

# Check if the last commit message is "Updated CHANGELOG.md"
LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
if [ "$LAST_COMMIT_MSG" != "Updated CHANGELOG.md" ]; then
    echo "Last commit message is not 'Updated CHANGELOG.md'"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(poetry version | cut -d' ' -f2)
echo "CURRENT_VERSION=$CURRENT_VERSION" >> $GITHUB_OUTPUT

# Bump version
if [ "$TEST_MODE" = "true" ]; then
    echo "TEST MODE: Would bump version from $CURRENT_VERSION"
    NEW_VERSION=$CURRENT_VERSION
else
    # Bump minor version
    poetry version minor
    NEW_VERSION=$(poetry version | cut -d' ' -f2)
fi

echo "NEW_VERSION=$NEW_VERSION" >> $GITHUB_OUTPUT 
