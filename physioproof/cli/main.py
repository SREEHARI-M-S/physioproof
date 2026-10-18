from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.panel import Panel

from physioproof.report.evidence import demo_scores
from physioproof.rppg.extract import estimate_dominant_bpm, synthetic_pulse_signal

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
) -> None:
    if not demo:
        console.print("Use --demo for now, or pass a video path in a future release.")
        raise typer.Exit(code=0)
    scores = demo_scores()
    if json_out:
        console.print(
            json.dumps(
                {
                    "heart_signal": scores.heart_signal,
                    "respiration": scores.respiration,
                    "temporal_coherence": scores.temporal_coherence,
                    "spatial_coherence": scores.spatial_coherence,
                    "overall_label": scores.overall_label,
                },
                indent=2,
            ),
        )
        return
    body = (
        f"Heart signal:        {scores.heart_signal:.0f}%\n"
        f"Respiration:           {scores.respiration:.0f}%\n"
        f"Temporal coherence:    {scores.temporal_coherence:.0f}%\n"
        f"Spatial coherence:     {scores.spatial_coherence:.0f}%\n\n"
        f"Overall: {scores.overall_label}"
    )
    console.print(Panel(body, title="VIDEO AUTHENTICITY REPORT"))


@app.command()
def signal(
    demo: bool = typer.Option(False, "--demo", help="Analyze synthetic rPPG demo trace"),
    fps: float = typer.Option(30.0, help="Frames per second for demo signal"),
    seconds: float = typer.Option(10.0, help="Demo trace length in seconds"),
    json_out: bool = typer.Option(False, "--json", help="Print analysis as JSON"),
) -> None:
    """Estimate heart rate from a 1-D physiological trace (demo uses synthetic rPPG)."""
    if not demo:
        console.print("Use --demo for now, or pass a trace file in a future release.")
        raise typer.Exit(code=0)
    length = max(8, int(fps * seconds))
    trace = synthetic_pulse_signal(length, fps=fps, bpm=72.0)
    bpm = estimate_dominant_bpm(trace, fps=fps)
    payload = {"fps": fps, "samples": length, "estimated_bpm": round(bpm, 1)}
    if json_out:
        console.print(json.dumps(payload, indent=2))
        return
    console.print(Panel(f"Estimated BPM: {payload['estimated_bpm']}", title="rPPG signal (demo)"))


if __name__ == "__main__":
    app()
