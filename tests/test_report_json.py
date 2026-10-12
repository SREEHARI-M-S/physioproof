from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_report_demo_json() -> None:
    result = runner.invoke(app, ["report", "--demo", "--json"])
    assert result.exit_code == 0
    assert "overall_label" in result.stdout
