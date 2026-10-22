import json
from pathlib import Path

from typer.testing import CliRunner

from physioproof.cli.main import app
from physioproof.rppg.extract import synthetic_pulse_signal
from physioproof.rppg.io import load_trace_file

runner = CliRunner()


def test_load_trace_json_array(tmp_path: Path) -> None:
    samples = synthetic_pulse_signal(120, fps=30.0, bpm=80.0)
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(samples.tolist()), encoding="utf-8")
    loaded = load_trace_file(path)
    assert loaded.shape == samples.shape


def test_signal_cli_reads_trace_csv(tmp_path: Path) -> None:
    samples = synthetic_pulse_signal(300, fps=30.0, bpm=72.0)
    path = tmp_path / "pulse.csv"
    path.write_text("value\n" + "\n".join(f"{x:.6f}" for x in samples), encoding="utf-8")
    result = runner.invoke(app, ["signal", "--trace", str(path), "--json", "--expect-bpm", "72"])
    assert result.exit_code == 0
    assert '"samples": 300' in result.stdout
    assert "pulse.csv" in result.stdout
    assert '"bpm_within_tolerance": true' in result.stdout
