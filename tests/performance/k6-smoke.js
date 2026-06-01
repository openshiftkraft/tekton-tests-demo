import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

export const options = {
  vus: Number(__ENV.VUS || 5),
  duration: __ENV.DURATION || '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
    checks: ['rate>0.99'],
  },
};

const addDuration = new Trend('add_duration');
const addFailures = new Rate('add_failures');
const baseUrl = __ENV.BASE_URL || 'http://localhost:8080';

export default function () {
  const health = http.get(`${baseUrl}/health`);
  check(health, {
    'health status is 200': (r) => r.status === 200,
  });

  const payload = JSON.stringify({ a: 20, b: 22 });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const add = http.post(`${baseUrl}/add`, payload, params);
  const ok = check(add, {
    'add status is 200': (r) => r.status === 200,
    'add response is 42': (r) => JSON.parse(r.body).result === 42,
  });
  addDuration.add(add.timings.duration);
  addFailures.add(!ok);
  sleep(1);
}

function junit(summary) {
  const failed = summary.metrics.http_req_failed?.values?.rate >= 0.01 ||
                 summary.metrics.http_req_duration?.values?.['p(95)'] >= 500 ||
                 summary.metrics.checks?.values?.rate <= 0.99;
  const failure = failed ? `<failure message="k6 thresholds failed">See k6-summary.json for full metrics.</failure>` : '';
  return `<?xml version="1.0" encoding="UTF-8"?>\n<testsuite name="k6-performance" tests="1" failures="${failed ? 1 : 0}">\n  <testcase classname="performance" name="k6 smoke thresholds">${failure}</testcase>\n</testsuite>\n`;
}

function allureResult(summary) {
  const failed = summary.metrics.http_req_failed?.values?.rate >= 0.01 ||
                 summary.metrics.http_req_duration?.values?.['p(95)'] >= 500 ||
                 summary.metrics.checks?.values?.rate <= 0.99;
  return JSON.stringify({
    uuid: `k6-${Date.now()}`,
    historyId: 'k6-performance-smoke',
    name: 'k6 performance smoke thresholds',
    fullName: 'performance.k6-smoke',
    status: failed ? 'failed' : 'passed',
    stage: 'finished',
    labels: [
      { name: 'suite', value: 'performance' },
      { name: 'framework', value: 'k6' },
      { name: 'language', value: 'javascript' }
    ],
    attachments: [
      { name: 'k6 summary', source: 'k6-summary.json', type: 'application/json' }
    ],
    start: Date.now(),
    stop: Date.now()
  }, null, 2);
}

export function handleSummary(data) {
  return {
    '/workspace/reports/performance-junit.xml': junit(data),
    '/workspace/reports/k6-summary.json': JSON.stringify(data, null, 2),
    '/workspace/allure-results/k6-performance-result.json': allureResult(data),
    stdout: JSON.stringify({
      checks_rate: data.metrics.checks?.values?.rate,
      http_req_failed_rate: data.metrics.http_req_failed?.values?.rate,
      p95_ms: data.metrics.http_req_duration?.values?.['p(95)']
    }, null, 2),
  };
}
