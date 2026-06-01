# Tekton + OpenShift + Allure End-to-End Testing Demo

This repository is a complete demo for orchestrating unit, functional, and performance tests in Tekton on OpenShift and publishing the results to Allure.

## What is included

- **Application**: Python FastAPI service with `/health`, `/version`, and `/add` endpoints.
- **Unit tests**: `pytest`, coverage XML, JUnit XML, and Allure results.
- **Functional tests**: `pytest` + `requests` against the deployed OpenShift route.
- **Performance tests**: `k6` smoke load test with thresholds, JUnit XML, JSON summary, and an Allure-compatible result.
- **Tekton pipeline**:
  1. Clone source
  2. Run unit tests
  3. Build and push container image with Buildah
  4. Deploy to OpenShift
  5. Run functional tests
  6. Run k6 performance test
  7. Summarize result locations
- **Allure service**: OpenShift Deployment, Service, Route, and PVC-backed raw-result storage.

## Repository layout

```text
app/                         FastAPI application
openshift/                   Namespace, RBAC, Allure, app deployment template
tekton/                      Tekton Tasks, Pipeline, PipelineRun template
tests/unit/                  Unit tests
tests/functional/            API functional tests
tests/performance/           k6 performance test
scripts/bootstrap.sh         OpenShift bootstrap + PipelineRun creation
scripts/run-local.sh         Local test runner
```

## Prerequisites

On the OpenShift cluster:

- Red Hat OpenShift Pipelines / Tekton Pipelines installed.
- OpenShift internal image registry available.
- A default StorageClass that can provision PVCs.
- Permission to create namespace resources.
- For the Buildah task, the `pipeline` ServiceAccount usually needs a compatible SCC. In many OpenShift Pipelines installations this is already handled. If the Buildah task fails with permission errors, a cluster admin can run:

```bash
oc adm policy add-scc-to-user privileged -z pipeline -n tekton-allure-demo
```

## Quick start

1. Push this repository to a Git server reachable from the OpenShift cluster.

2. Log in with `oc`:

```bash
oc login ...
```

3. Run:

```bash
GIT_URL=https://github.com/YOUR_ORG/tekton-allure-demo.git \
GIT_REVISION=main \
./scripts/bootstrap.sh
```

4. Watch the run:

```bash
tkn pipelinerun list -n tekton-allure-demo
tkn pipelinerun logs -n tekton-allure-demo -f --last
```

5. Open the app and Allure routes:

```bash
oc get route demo-api -n tekton-allure-demo
oc get route allure -n tekton-allure-demo
```

## Applying resources manually

```bash
oc apply -f openshift/00-namespace.yaml
oc apply -f openshift/01-rbac.yaml
oc apply -f openshift/02-allure.yaml
oc apply -f tekton/tasks.yaml
oc apply -f tekton/pipeline.yaml

sed 's|GIT_URL_PLACEHOLDER|https://github.com/YOUR_ORG/tekton-allure-demo.git|g' \
  tekton/pipelinerun-template.yaml | oc create -f -
```

## Result model

The demo uses two reporting layers:

1. **Tekton status and task results**
   - PipelineRun/TaskRun status tells you whether the CI gate passed or failed.
   - Task results expose `unit-status`, `functional-status`, `performance-status`, `app-url`, and `allure-url`.

2. **Allure raw results**
   - Unit test raw results: `/app/allure-results/unit`
   - Functional test raw results: `/app/allure-results/functional`
   - Performance test raw result: `/app/allure-results/performance`

The Allure Docker Service watches the mounted PVC and refreshes reports when new raw results appear.

## Notes and production hardening

This is intentionally a concise demo. For production, consider:

- Store raw Allure results in object storage or a shared RWX volume.
- Use Tekton Results for long-term PipelineRun/TaskRun history.
- Add Tekton Chains for signed build provenance.
- Use a proper image tag instead of `latest`, e.g. Git SHA or PipelineRun name.
- Split smoke, regression, and performance stages by trigger type.
- Replace privileged Buildah with your organization’s approved build strategy if needed.
- Add NetworkPolicies, resource limits, and Route TLS.

## Local run

```bash
./scripts/run-local.sh
```

To view local Allure results, install Allure CLI and run:

```bash
allure serve allure-results
```
