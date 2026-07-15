def should_switch(current_course, ranking):
    
    best_course = ranking[0][0]
    best_score = ranking[0][1]

    if current_course == best_course:
        return False, "✅ 現状維持"

    current_score = 0

    for course, score in ranking:
        if course == current_course:
            current_score = score
            break

    if best_score - current_score < 15:
        return False, "🤔 変更メリット小"

    return True, f"🔄 {best_course}へ変更"