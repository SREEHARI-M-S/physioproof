from physioproof.rppg.extract import estimate_dominant_bpm, synthetic_pulse_signal


def test_estimate_dominant_bpm_near_seeded_rate() -> None:
    trace = synthetic_pulse_signal(900, fps=30.0, bpm=72.0)
    bpm = estimate_dominant_bpm(trace, fps=30.0)
    assert 68 <= bpm <= 76
