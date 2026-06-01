#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-tekton-allure-demo}
GIT_URL=${GIT_URL:-}
GIT_REVISION=${GIT_REVISION:-main}

if [[ -z "${GIT_URL}" ]]; then
  echo "Set GIT_URL to the Git repository URL containing this demo before running." >&2
  echo "Example: GIT_URL=https://github.com/your-org/tekton-allure-demo.git ./scripts/bootstrap.sh" >&2
  exit 1
fi

oc apply -f openshift/00-namespace.yaml
oc apply -f openshift/01-rbac.yaml
oc apply -f openshift/02-allure.yaml
oc apply -f tekton/tasks.yaml
oc apply -f tekton/pipeline.yaml

TMP=$(mktemp)
sed \
  -e "s|GIT_URL_PLACEHOLDER|${GIT_URL}|g" \
  -e "s|value: main|value: ${GIT_REVISION}|" \
  tekton/pipelinerun-template.yaml > "${TMP}"

oc create -f "${TMP}"
rm -f "${TMP}"

echo "PipelineRun created. Watch with:"
echo "  tkn pipelinerun list -n ${NAMESPACE}"
echo "  tkn pipelinerun logs -n ${NAMESPACE} -f --last"
echo "Allure route:"
echo "  oc get route allure -n ${NAMESPACE}"
