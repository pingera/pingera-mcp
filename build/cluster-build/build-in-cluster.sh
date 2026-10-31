#!/bin/bash
# Builds the pingera-mcp-server image inside the cluster with Kaniko and pushes it to the
# registry. Build + push only (no deploy). Same flow as the backend's
# build_and_deploy/cluster-build/build-in-cluster.sh, and uses the same `builds` namespace and secrets.
#
# Usage: build-in-cluster.sh VERSION [--no-tag]
#   VERSION    image tag / git tag to build (required); must match pingera_mcp.__version__
#   --no-tag   don't create the git tag (build a tag that is already pushed)
#
# If the git tag already exists on origin (for example pushed to release the package), it is built
# as is. Pushing a new tag also triggers the PyPI release workflow (.github/workflows/release.yml).
# Uses the current kubectl context; set KUBE_CONTEXT to choose another.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
POD_TEMPLATE="${SCRIPT_DIR}/kaniko-build-pod.yaml"

NAMESPACE="builds"
REGISTRY="cr.yandex/crpaui11dg2kd5vqkq99"
IMAGE_NAME="pingera-mcp-server"
REPO_URL="github.com/pingera/pingera-mcp.git"

TAG="${1:-}"
CREATE_TAG=true
if [[ "${2:-}" == "--no-tag" ]]; then
  CREATE_TAG=false
fi

if [[ -z "${TAG}" ]]; then
  echo "Usage: $0 VERSION [--no-tag]" >&2
  exit 1
fi

KUBECTL=(kubectl)
if [[ -n "${KUBE_CONTEXT:-}" ]]; then
  KUBECTL+=(--context "${KUBE_CONTEXT}")
fi
echo "Building ${REGISTRY}/${IMAGE_NAME}:${TAG} in kubectl context '$("${KUBECTL[@]}" config current-context)'"

for secret in git-pat kaniko-registry-push; do
  if ! "${KUBECTL[@]}" -n "${NAMESPACE}" get secret "${secret}" >/dev/null 2>&1; then
    echo "Error: secret ${NAMESPACE}/${secret} not found. Run pingera-backend's" \
      "build_and_deploy/cluster-build/setup-build-namespace.sh first." >&2
    exit 1
  fi
done

# Kaniko clones the tag, so it must exist on origin.
if git -C "${REPO_ROOT}" ls-remote --exit-code --tags origin "refs/tags/${TAG}" >/dev/null 2>&1; then
  echo "Tag ${TAG} already exists on origin; building it."
elif [[ "${CREATE_TAG}" == "true" ]]; then
  VERSION="$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "${REPO_ROOT}/pingera_mcp/__init__.py")"
  if [[ "${VERSION}" != "${TAG}" ]]; then
    echo "Error: pingera_mcp.__version__ is ${VERSION}, not ${TAG}. Bump the version first." >&2
    exit 1
  fi
  if [[ -n "$(git -C "${REPO_ROOT}" status --porcelain --untracked-files=no)" ]]; then
    echo "Error: uncommitted changes; the image is built from the committed tree only." >&2
    exit 1
  fi
  git -C "${REPO_ROOT}" tag -a "${TAG}" -m "Release ${TAG}"
  git -C "${REPO_ROOT}" push origin "${TAG}"
else
  echo "Error: tag ${TAG} is not on origin (drop --no-tag to create it)." >&2
  exit 1
fi

POD_NAME="${IMAGE_NAME}-build-$(date +%s)"

# Render the pod manifest with this build's values.
MANIFEST="$(sed \
  -e "s|__NAME__|${POD_NAME}|g" \
  -e "s|__REPO_URL__|${REPO_URL}|g" \
  -e "s|__TAG__|${TAG}|g" \
  -e "s|__REGISTRY__|${REGISTRY}|g" \
  -e "s|__IMAGE_NAME__|${IMAGE_NAME}|g" \
  "${POD_TEMPLATE}")"

# Always clean up the build pod on exit.
cleanup() {
  "${KUBECTL[@]}" -n "${NAMESPACE}" delete pod "${POD_NAME}" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "${MANIFEST}" | "${KUBECTL[@]}" apply -f -

echo "Waiting for build pod ${POD_NAME} to start..."
"${KUBECTL[@]}" -n "${NAMESPACE}" wait --for=condition=Ready "pod/${POD_NAME}" --timeout=120s \
  || "${KUBECTL[@]}" -n "${NAMESPACE}" wait --for=jsonpath='{.status.phase}'=Succeeded "pod/${POD_NAME}" --timeout=1s \
  || true

# Stream Kaniko logs.
"${KUBECTL[@]}" -n "${NAMESPACE}" logs -f "${POD_NAME}" || true

# Wait for completion and capture the real exit status.
echo "Waiting for build to finish..."
if "${KUBECTL[@]}" -n "${NAMESPACE}" wait --for=jsonpath='{.status.phase}'=Succeeded \
     "pod/${POD_NAME}" --timeout=1800s; then
  echo "Successfully built and pushed: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
  exit 0
else
  echo "Build failed for ${REGISTRY}/${IMAGE_NAME}:${TAG}" >&2
  "${KUBECTL[@]}" -n "${NAMESPACE}" describe "pod/${POD_NAME}" || true
  exit 1
fi
