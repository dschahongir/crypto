def calculate_confidence(phase, ao, bb_width):
    score = 0

    if phase == "ENTRY":
        score += 40
    if ao > 0:
        score += 20
    if bb_width < 0.06:
        score += 20

    return min(score, 95)