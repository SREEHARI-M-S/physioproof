import json
from pathlib import Path

from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_signal_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "analysis.json"
    result = runner.invoke(app, ["signal", "--demo", "-o", str(out)])
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["source"] == "demo"
    assert "estimated_bpm" in payload


def test_diagnose_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "diagnose.json"
    result = runner.invoke(app, ["diagnose", "--demo", "-o", str(out)])
    assert result.exit_code == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["passed"] is False
    assert payload["issues"]
