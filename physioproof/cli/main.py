from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.panel import Panel

from physioproof.report.evidence import demo_scores

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


if __name__ == "__main__":
    app()
