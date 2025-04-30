#!/bin/bash

# Create and push tag
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin "v$NEW_VERSION"

# Merge develop into main
git checkout main
git merge develop
git push origin main 
