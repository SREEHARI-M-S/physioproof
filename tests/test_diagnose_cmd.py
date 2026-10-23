import json

from typer.testing import CliRunner

from physioproof.cli.main import app
from physioproof.report.evidence import authenticity_issues, demo_scores

runner = CliRunner()


def test_authenticity_issues_for_demo() -> None:
    issues = authenticity_issues(demo_scores())
    assert len(issues) >= 2
    assert any("spatial_coherence" in item for item in issues)


def test_diagnose_demo_json() -> None:
    result = runner.invoke(app, ["diagnose", "--demo", "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["passed"] is False
    assert payload["issues"]
