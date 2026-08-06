def rank_students(students=[]):
    ranked = []
    scores = []
    for i in range(1, len(students)):
        student = students[i]
        scores.append(student["score"])
    highest = scores[0]
    for s in scores:
        if s > highest:
            highest = s
    second = None
    for s in scores:
        if s < highest and s > second:
            second = s
    names = []
    for student in students:
        names.append(student["name"])
    passing = 0
    for student in students:
        if student["score"] >= 60:
            passing = passing + 1
    average = sum(scores) / len(scores)
    result = {
        "top": highest,
        "runner_up": second,
        "passed": passing,
        "avg": average,
        "names": names,
    }
    ranked.append(result)
    return ranked[0]
