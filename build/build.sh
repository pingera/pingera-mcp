# run as bash build/build.sh VERSION
# example bash build/build.sh 1.0.4

# rm previous builds from dist folder (optional)
#rm -rf dist/*

TAG="${1}"

# build uv package
uv build --version "${TAG}"

# publish to pypi
uv publish --token `echo $PYPI_TOKEN`

# create git tag
git tag -a "${TAG}" -m "Release ${TAG}"
git push origin "${TAG}"
