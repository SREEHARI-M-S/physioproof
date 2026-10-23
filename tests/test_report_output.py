import json
from pathlib import Path

from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_report_writes_json_file(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    result = runner.invoke(app, ["report", "--demo", "-o", str(out)])
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "overall_label" in payload
    assert "LIKELY MANIPULATED" in payload["overall_label"]


def test_check_json_includes_issues_on_failure() -> None:
    result = runner.invoke(app, ["check", "--demo", "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["issues"]
