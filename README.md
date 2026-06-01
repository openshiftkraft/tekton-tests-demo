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
  3. Build the container image with OpenShift Builds
  4. Deploy to OpenShift
  5. Run functional tests
  6. Run k6 performance test
  7. Generate the Allure HTML report
  8. Summarize result locations
- **Allure report server**: OpenShift Deployment, Service, and Route serving the generated Allure HTML report from PVC storage.

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
- No privileged Tekton Task is required. The image build uses OpenShift Builds with a DockerStrategy binary build, so the Tekton pod only needs permission to create and start BuildConfigs/Builds.

## Quick start

1. Push this repository to a Git server reachable from the OpenShift cluster.

2. Log in with `oc`:

```bash
oc login ...
```

3. Run:

```bash
GIT_URL=https://github.com/openshiftkraft/tekton-tests-demo.git \
GIT_REVISION=main \
./scripts/bootstrap.sh
```

4. Watch the run:

```bash
tkn pipelinerun list -n tekton-allure-demo
tkn pipelinerun logs -n tekton-allure-demo -f --last
```

5. Open the app and Allure report routes:

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

sed 's|GIT_URL_PLACEHOLDER|https://github.com/openshiftkraft/tekton-tests-demo.git|g' \
  tekton/pipelinerun-template.yaml | oc create -f -
```

## Result model

The demo uses three reporting layers:

1. **Tekton status and task results**
   - PipelineRun/TaskRun status tells you whether the CI gate passed or failed.
   - Task results expose `unit-status`, `functional-status`, `performance-status`, `report-status`, `app-url`, and `allure-url`.

2. **Allure raw results**
   - Unit test raw results: `allure-results/unit`
   - Functional test raw results: `allure-results/functional`
   - Performance test raw result: `allure-results/performance`

3. **Generated Allure HTML report**
   - The `generate-allure-report` Tekton task collects raw Allure result files, preserves report history, generates static Allure HTML, and writes it to the shared PVC under `allure-report`.
   - The `allure` OpenShift Route exposes that generated report directly through an unprivileged nginx container.

After a successful PipelineRun, open:

```bash
oc get route allure -n tekton-allure-demo
```

Then browse to the returned host. You should see the normal Allure report UI immediately, without calling `/generate-report` or `/latest-report`.

## Notes and production hardening

This is intentionally a concise demo. For production, consider:

- Store raw Allure results and generated report history in object storage or a shared RWX volume.
- Use Tekton Results for long-term PipelineRun/TaskRun history.
- Add Tekton Chains for signed build provenance.
- Use a proper image tag instead of `latest`, e.g. Git SHA or PipelineRun name.
- Split smoke, regression, and performance stages by trigger type.
- For production, replace the demo OpenShift BuildConfig with your organization’s approved build strategy if different, such as Shipwright, Buildpacks, or a managed build service.
- Add NetworkPolicies, resource limits, and Route TLS.

## Local run

```bash
./scripts/run-local.sh
```

To view local Allure results, install Allure CLI and run:

```bash
allure serve allure-results
```
