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
