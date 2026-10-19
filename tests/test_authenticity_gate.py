from physioproof.report.evidence import demo_scores, passes_authenticity_gate


def test_demo_scores_fail_default_gate() -> None:
    scores = demo_scores()
    assert passes_authenticity_gate(scores) is False


def test_high_spatial_passes_gate() -> None:
    scores = demo_scores()
    scores.spatial_coherence = 80.0
    assert passes_authenticity_gate(scores) is True
