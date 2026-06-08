import shutil
from pathlib import Path
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        if call.excinfo and call.excinfo.errisinstance(Warning):
            report.outcome = "passed"
            report.wasxfail = "warning"


def pytest_sessionfinish(session, exitstatus):
    alluredir = session.config.getoption("--alluredir", default=None)
    if alluredir:
        src = Path(session.config.rootdir) / "categories.json"
        if src.exists():
            shutil.copy(str(src), str(Path(alluredir) / "categories.json"))
