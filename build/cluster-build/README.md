# In-cluster image builds (Kaniko)

Build the `pingera-mcp-server` Docker image inside the product cluster, the same way the backend image is built
(`pingera-backend/build_and_deploy/cluster-build`). A one-shot [Kaniko](https://github.com/GoogleContainerTools/kaniko)
pod clones this repo at a pushed git tag, builds the `Dockerfile` and pushes
`cr.yandex/crpaui11dg2kd5vqkq99/pingera-mcp-server:<version>` (and `:latest`). Build + push only, no rollout.

## One-time setup

Uses the backend's `builds` namespace and its `git-pat` and `kaniko-registry-push` secrets. If they don't exist yet,
run `setup-build-namespace.sh` from `pingera-backend/build_and_deploy/cluster-build` once.

## Build

```bash
# bump pingera_mcp/__init__.py to the new version and commit, then:
build/cluster-build/build-in-cluster.sh 0.2.0            # tag the current commit, push the tag, build it
build/cluster-build/build-in-cluster.sh 0.2.0 --no-tag   # build a tag that is already pushed
KUBE_CONTEXT=<context> build/cluster-build/build-in-cluster.sh 0.2.0   # use another kubectl context
```

The script checks that the version matches `pingera_mcp.__version__` and that the tree is committed, tags and pushes
the commit (unless the tag already exists on origin, e.g. because the release was already tagged), launches
the build pod, streams its logs, waits for it and deletes the pod on exit.

Then set the image in `pingera-backend/build_and_deploy/deploy_app/mcp/mcp_deployment.yaml` and apply it.

## Notes

- A version tag also triggers the PyPI release workflow (`.github/workflows/release.yml`), so one tag releases both
  the package and the image. If you tag first (`git tag 0.2.0 && git push origin 0.2.0`), run this script afterwards;
  it builds the existing tag.

- Kaniko clones the committed tree at the tag, so uncommitted changes are never built.
- Builds run on the amd64 `supporting-apps` nodes (`nodeSelector` in the pod template), so the image is amd64.
