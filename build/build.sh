#!/bin/bash
# run as bash build/build.sh VERSION
# example bash build/build.sh 1.0.7

TAG="${1}"

if [ -z "$TAG" ]; then
    echo "Error: Version tag is required"
    echo "Usage: bash build/build.sh 0.1.7"
    exit 1
fi

echo "Building version: $TAG"

# Clean previous builds from dist folder
rm -rf dist/*

# Update version in source code
sed -i "s/__version__ = \".*\"/__version__ = \"${TAG}\"/" pingera_mcp/__init__.py

# Build uv package
uv build

# Publish to pypi
uv publish --token `echo $PYPI_TOKEN`

# Create git tag
git tag -a "${TAG}" -m "Release ${TAG}"
git push origin "${TAG}"
