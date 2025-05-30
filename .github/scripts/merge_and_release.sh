#!/bin/bash

# Commit version changes to develop
git add pyproject.toml
git commit -m "Release version $NEW_VERSION"
git push origin develop

# Merge develop into main
git checkout main
git merge develop
git push origin main

# Create and push tag from main
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin "v$NEW_VERSION"
 