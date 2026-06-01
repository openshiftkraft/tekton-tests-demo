#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r app/requirements.txt -r requirements-test.txt
pytest tests/unit --junitxml=reports/unit-junit.xml --cov=app --cov-report=xml:reports/coverage.xml --alluredir=allure-results/unit
uvicorn app.main:app --host 127.0.0.1 --port 8080 &
PID=$!
trap 'kill ${PID}' EXIT
BASE_URL=http://127.0.0.1:8080 pytest tests/functional --junitxml=reports/functional-junit.xml --alluredir=allure-results/functional
if command -v k6 >/dev/null 2>&1; then
  BASE_URL=http://127.0.0.1:8080 k6 run tests/performance/k6-smoke.js || true
fi
