# def calculate_confidence(phase, ao, bb_width):
#     score = 0

#     if phase == "ENTRY":
#         score += 40
#     if ao > 0:
#         score += 20
#     if bb_width < 0.06:
#         score += 20

#     return min(score, 95)


def calculate_confidence(phase, ao, bb_width):
    score = 0

    if phase == "ENTRY":
        score += 45

    if ao > 0:
        score += 25

    # не требуем "супер-сжатие", а даем баллы за адекватную ширину
    if bb_width < 0.08:
        score += 20
    elif bb_width < 0.12:
        score += 10

    return min(score, 95)