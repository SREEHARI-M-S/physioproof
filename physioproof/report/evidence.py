from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceScores(BaseModel):
    heart_signal: float = Field(ge=0, le=100)
    respiration: float = Field(ge=0, le=100)
    temporal_coherence: float = Field(ge=0, le=100)
    spatial_coherence: float = Field(ge=0, le=100)

    @property
    def overall_label(self) -> str:
        if self.spatial_coherence < 50:
            return "LIKELY MANIPULATED"
        avg = (
            self.heart_signal
            + self.respiration
            + self.temporal_coherence
            + self.spatial_coherence
        ) / 4.0
        if avg >= 75:
            return "LIKELY AUTHENTIC"
        if avg >= 50:
            return "UNCERTAIN"
        return "LIKELY MANIPULATED"


def demo_scores() -> EvidenceScores:
    return EvidenceScores(
        heart_signal=94.0,
        respiration=81.0,
        temporal_coherence=89.0,
        spatial_coherence=38.0,
    )


def passes_authenticity_gate(scores: EvidenceScores, min_spatial: float = 50.0) -> bool:
    """Return True when demo scores are not flagged as likely manipulated."""
    return scores.spatial_coherence >= min_spatial and scores.overall_label != "LIKELY MANIPULATED"


def authenticity_issues(scores: EvidenceScores, min_spatial: float = 50.0) -> list[str]:
    """Human-readable reasons the authenticity gate would fail."""
    issues: list[str] = []
    if scores.spatial_coherence < min_spatial:
        issues.append(
            f"spatial_coherence {scores.spatial_coherence:.0f} is below minimum {min_spatial:.0f}",
        )
    if scores.overall_label == "LIKELY MANIPULATED":
        issues.append(f"overall_label is {scores.overall_label}")
    return issues
