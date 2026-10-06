from physioproof.report.evidence import demo_scores


def test_demo_scores_label() -> None:
    scores = demo_scores()
    assert scores.overall_label == "LIKELY MANIPULATED"
