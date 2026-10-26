from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from physioproof.report.evidence import authenticity_issues, demo_scores, passes_authenticity_gate
from physioproof.rppg.extract import estimate_dominant_bpm, synthetic_pulse_signal
from physioproof.rppg.io import load_trace_file

app = typer.Typer(no_args_is_help=True, help="PhysioProof — physiological video evidence")
console = Console()


@app.command()
def version() -> None:
    from physioproof import __version__

    console.print(f"physioproof {__version__}")


@app.command()
def report(
    demo: bool = typer.Option(False, "--demo", help="Print sample evidence report"),
    json_out: bool = typer.Option(False, "--json", help="Print report as JSON"),
    output: Path | None = typer.Option(
        None,
        "-o",
        "--output",
        help="Write JSON report to this file (implies structured output)",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit 1 when demo scores fail authenticity gate (CI-friendly)",
    ),
) -> None:
    if not demo:
        console.print("Use --demo for now, or pass a video path in a future release.")
        raise typer.Exit(code=0)
    scores = demo_scores()
    gate_passed = passes_authenticity_gate(scores)
    report_payload: dict[str, object] = {
        "heart_signal": scores.heart_signal,
        "respiration": scores.respiration,
        "temporal_coherence": scores.temporal_coherence,
        "spatial_coherence": scores.spatial_coherence,
        "overall_label": scores.overall_label,
        "gate_passed": gate_passed,
    }
    if not gate_passed:
        report_payload["gate_issues"] = authenticity_issues(scores)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(report_payload, indent=2))
    elif output is None:
        body = (
            f"Heart signal:        {scores.heart_signal:.0f}%\n"
            f"Respiration:           {scores.respiration:.0f}%\n"
            f"Temporal coherence:    {scores.temporal_coherence:.0f}%\n"
            f"Spatial coherence:     {scores.spatial_coherence:.0f}%\n\n"
            f"Overall: {scores.overall_label}"
        )
        console.print(Panel(body, title="VIDEO AUTHENTICITY REPORT"))
    if strict and not gate_passed:
        raise typer.Exit(code=1)


@app.command()
def diagnose(
    demo: bool = typer.Option(False, "--demo", help="Explain demo authenticity gate failures"),
    json_out: bool = typer.Option(False, "--json", help="Print diagnosis as JSON"),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write diagnosis JSON to file"),
    min_spatial: float = typer.Option(50.0, help="Minimum spatial coherence to pass gate"),
) -> None:
    """List why demo scores fail the authenticity gate (empty when gate passes)."""
    if not demo:
        console.print("Use --demo for now.")
        raise typer.Exit(code=0)
    scores = demo_scores()
    passed = passes_authenticity_gate(scores, min_spatial=min_spatial)
    issues = authenticity_issues(scores, min_spatial=min_spatial)
    payload = {
        "passed": passed,
        "overall_label": scores.overall_label,
        "issues": issues,
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(payload, indent=2))
    elif output is None:
        if issues:
            for item in issues:
                console.print(f"[yellow]•[/yellow] {item}")
        else:
            console.print("[green]No gate issues[/green]")
    raise typer.Exit(code=0 if passed else 1)


@app.command()
def check(
    demo: bool = typer.Option(False, "--demo", help="Run demo authenticity gate"),
    json_out: bool = typer.Option(False, "--json", help="Print gate result as JSON"),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write gate result JSON to file"),
) -> None:
    """Exit 0 when demo scores pass the authenticity gate (for CI)."""
    if not demo:
        console.print("Use --demo for now.")
        raise typer.Exit(code=0)
    scores = demo_scores()
    passed = passes_authenticity_gate(scores)
    payload: dict[str, object] = {
        "passed": passed,
        "overall_label": scores.overall_label,
        "spatial_coherence": scores.spatial_coherence,
    }
    if not passed:
        payload["issues"] = authenticity_issues(scores)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(payload, indent=2))
    elif output is None:
        if passed:
            console.print("[green]PASS[/green] authenticity gate")
        else:
            console.print("[red]FAIL[/red] authenticity gate")
    raise typer.Exit(code=0 if passed else 1)


@app.command()
def signal(
    demo: bool = typer.Option(False, "--demo", help="Analyze synthetic rPPG demo trace"),
    trace: Path | None = typer.Option(
        None,
        "--trace",
        exists=True,
        dir_okay=False,
        readable=True,
        help="CSV or JSON file with at least 8 samples",
    ),
    fps: float = typer.Option(30.0, help="Frames per second for demo signal"),
    seconds: float = typer.Option(10.0, help="Demo trace length in seconds"),
    json_out: bool = typer.Option(False, "--json", help="Print analysis as JSON"),
    expect_bpm: float | None = typer.Option(
        None,
        "--expect-bpm",
        help="Fail when estimated BPM differs by more than tolerance",
    ),
    tolerance: float = typer.Option(5.0, help="Allowed BPM delta when using --expect-bpm"),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write analysis JSON to file"),
) -> None:
    """Estimate heart rate from a 1-D physiological trace (demo uses synthetic rPPG)."""
    trace_path = trace
    if trace_path is not None:
        try:
            signal_samples = load_trace_file(trace_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise typer.BadParameter(str(exc)) from exc
        length = int(signal_samples.size)
        source = str(trace_path)
    elif demo:
        length = max(8, int(fps * seconds))
        signal_samples = synthetic_pulse_signal(length, fps=fps, bpm=72.0)
        source = "demo"
    else:
        console.print("Use --demo or pass --trace <file.csv|.json>.")
        raise typer.Exit(code=0)
    bpm = estimate_dominant_bpm(signal_samples, fps=fps)
    payload: dict[str, object] = {
        "fps": fps,
        "samples": length,
        "source": source,
        "estimated_bpm": round(bpm, 1),
    }
    if expect_bpm is not None:
        delta = abs(float(payload["estimated_bpm"]) - expect_bpm)
        payload["expect_bpm"] = expect_bpm
        payload["bpm_within_tolerance"] = delta <= tolerance
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    if json_out:
        console.print(json.dumps(payload, indent=2))
    elif output is None:
        console.print(Panel(f"Estimated BPM: {payload['estimated_bpm']}", title="rPPG signal (demo)"))
    if expect_bpm is not None and not payload.get("bpm_within_tolerance"):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
