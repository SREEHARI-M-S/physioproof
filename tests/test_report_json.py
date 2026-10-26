from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


import json


def test_report_demo_json() -> None:
    result = runner.invoke(app, ["report", "--demo", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["gate_passed"] is False
    assert payload["gate_issues"]
