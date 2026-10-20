from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_check_demo_fails_gate() -> None:
    result = runner.invoke(app, ["check", "--demo", "--json"])
    assert result.exit_code == 1
    assert '"passed": false' in result.stdout
