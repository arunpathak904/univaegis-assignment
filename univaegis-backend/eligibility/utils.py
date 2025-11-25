from typing import Dict, Any, Tuple, List


def compute_eligibility(extracted_data: Dict[str, Any], ielts_scores: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Compute eligibility based on:
      - extracted academic data (percentage or GPA)
      - IELTS scores (listening, reading, writing, speaking)

    Returns:
      (is_eligible: bool, reasons: list of strings)
    """
    reasons: List[str] = []
    eligible = True

    # 1) Extract marks from document's extracted_data
    percentage = extracted_data.get("percentage")
    gpa = extracted_data.get("gpa")

    # If both are missing, we can't evaluate academic score
    if percentage is None and gpa is None:
        eligible = False
        reasons.append("No percentage or GPA found in the document.")
    else:
        # Apply academic rule: >=80% OR GPA >=8.0
        academic_ok = False
        if percentage is not None and percentage >= 80.0:
            academic_ok = True
        if gpa is not None and gpa >= 8.0:
            academic_ok = True

        if not academic_ok:
            eligible = False
            reasons.append("Academic score below threshold (need >=80% or GPA>=8.0).")

    # 2) IELTS rules
    required_bands = ["listening", "reading", "writing", "speaking"]
    for band in required_bands:
        val = ielts_scores.get(band)
        if val is None:
            eligible = False
            reasons.append(f"IELTS {band} score is missing.")
        elif val < 8.0:
            eligible = False
            reasons.append(f"IELTS {band} below 8.0 (got {val}).")

    return eligible, reasons
