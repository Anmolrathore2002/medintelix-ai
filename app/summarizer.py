def generate_summary(results, risk_score):
    abnormal = [f"{k} ({v})" for k, v in results.items() if v != "Normal"]

    if not abnormal:
        return "All parameters are within normal range. Health risk is minimal."

    return (
        f"Abnormal findings detected in: {', '.join(abnormal)}. "
        f"Overall Health Risk Score: {risk_score}%. "
        "Clinical consultation recommended."
    )