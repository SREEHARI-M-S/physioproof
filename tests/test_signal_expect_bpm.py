from typer.testing import CliRunner

from physioproof.cli.main import app

runner = CliRunner()


def test_signal_expect_bpm_passes_for_seeded_rate() -> None:
    result = runner.invoke(app, ["signal", "--demo", "--expect-bpm", "72", "--json"])
    assert result.exit_code == 0
    assert "bpm_within_tolerance" in result.stdout
