import json
from pathlib import Path

from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_scores_demo_json() -> None:
    result = runner.invoke(app, ["scores", "--demo", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["gate_passed"] is False
    assert payload["spatial_coherence"] == 38.0
