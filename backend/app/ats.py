"""ATS (Applicant Tracking System) Resume Scorer — PathForge Backend.

Scores a resume against a job description across 5 weighted dimensions:
  1. Keyword Match      (35%) — skill/keyword overlap with JD
  2. Format & Structure (20%) — sections, length, no tables/images
  3. Section Coverage   (20%) — presence of key resume sections
  4. Quantification     (15%) — numbers, metrics, impact statements
  5. Action Verbs       (10%) — strong opening verbs per bullet

Returns an overall ATS score (0-100) + per-dimension breakdown + tips.
"""

import re
from typing import Any
from difflib import SequenceMatcher


# ── Action verbs that ATS systems reward ─────────────────────────────────────
_ACTION_VERBS = {
    "achieved", "accelerated", "architected", "automated", "built",
    "collaborated", "created", "decreased", "delivered", "deployed",
    "designed", "developed", "drove", "engineered", "established",
    "executed", "expanded", "generated", "grew", "implemented",
    "improved", "increased", "integrated", "launched", "led",
    "managed", "mentored", "migrated", "optimized", "orchestrated",
    "owned", "pioneered", "produced", "reduced", "refactored",
    "released", "resolved", "scaled", "shipped", "spearheaded",
    "streamlined", "transformed", "trained", "upgraded", "utilized",
}

# ── Resume section keywords ───────────────────────────────────────────────────
_SECTION_PATTERNS = {
    "experience":    r'\b(experience|work\s*history|employment|positions?\s*held|career)\b',
    "education":     r'\b(education|academic|degree|university|college|school|qualification)\b',
    "skills":        r'\b(skills?|technical\s*skills?|competencies|technologies|expertise|proficiencies)\b',
    "summary":       r'\b(summary|objective|profile|about\s*me|overview|introduction)\b',
    "projects":      r'\b(projects?|portfolio|work\s*samples?|case\s*studies)\b',
    "certifications":r'\b(certifications?|certificates?|credentials?|licenses?|accreditations?)\b',
    "achievements":  r'\b(achievements?|accomplishments?|awards?|honors?|recognition)\b',
}

# ── Quantification patterns ───────────────────────────────────────────────────
_QUANT_PATTERNS = [
    r'\d+\s*%',                          # percentages: 40%, 3.5%
    r'\$\s*\d[\d,\.]*[kmb]?',           # money: $1.2M, $500k
    r'\d[\d,]*\s*(users?|customers?|clients?|requests?|transactions?)',
    r'\d[\d,]*\s*(hours?|days?|weeks?|months?)',
    r'(increased|decreased|reduced|improved|grew|saved|generated)\s+by\s+\d',
    r'\d+x\s*(faster|better|improvement|increase|growth)',
    r'(team\s*of|managed|led)\s+\d+',
    r'\d+\s*(projects?|products?|features?|services?|systems?)',
    r'(top|rank(ed)?)\s+\d+',
    r'\d+\s*(ms|seconds?|minutes?)\s*(latency|response|load)',
]

# ── Negative ATS signals ──────────────────────────────────────────────────────
_BAD_PATTERNS = [
    r'<table', r'<img', r'<div',         # HTML tables/images
    r'\|.*\|.*\|',                        # markdown tables
    r'[^\x00-\x7F]{5,}',                 # excessive non-ASCII (symbols/icons)
]


def _tokenize(text: str) -> set[str]:
    """Lowercase word tokens, 3+ chars."""
    return {w.lower() for w in re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\.]{2,}\b', text)}


def _fuzzy_overlap(resume_tokens: set[str], jd_tokens: set[str]) -> float:
    """Fraction of JD tokens found in resume (exact or fuzzy ≥0.85)."""
    if not jd_tokens:
        return 0.0
    matched = 0
    for jd_tok in jd_tokens:
        if jd_tok in resume_tokens:
            matched += 1
        else:
            for res_tok in resume_tokens:
                if SequenceMatcher(None, jd_tok, res_tok).ratio() >= 0.85:
                    matched += 1
                    break
    return matched / len(jd_tokens)


def score_ats(resume_text: str, jd_text: str, jd_skills: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute ATS score and return full breakdown with actionable tips.

    Returns:
        {
          "ats_score": int,           # 0-100 overall
          "dimensions": {             # per-dimension scores 0-100
            "keyword_match": int,
            "format_structure": int,
            "section_coverage": int,
            "quantification": int,
            "action_verbs": int,
          },
          "tips": list[str],          # actionable improvement tips
          "keyword_hits": list[str],  # JD keywords found in resume
          "keyword_misses": list[str],# JD keywords missing from resume
          "sections_found": list[str],
          "sections_missing": list[str],
        }
    """
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    resume_tokens = _tokenize(resume_text)
    jd_tokens = _tokenize(jd_text)
    tips: list[str] = []

    # ── 1. Keyword Match (35%) ────────────────────────────────────────────────
    # Use extracted JD skill names + raw JD token overlap
    jd_skill_names = [s["name"] for s in jd_skills if s.get("name")]

    keyword_hits: list[str] = []
    keyword_misses: list[str] = []

    for skill_name in jd_skill_names:
        skill_lower = skill_name.lower()
        # Exact or near-exact match in resume
        found = skill_lower in resume_lower
        if not found:
            # Fuzzy: check if any resume token is close
            for tok in resume_tokens:
                if SequenceMatcher(None, skill_lower, tok).ratio() >= 0.82:
                    found = True
                    break
        if found:
            keyword_hits.append(skill_name)
        else:
            keyword_misses.append(skill_name)

    # Also check raw token overlap for non-skill keywords
    raw_overlap = _fuzzy_overlap(resume_tokens, jd_tokens)

    skill_match_ratio = len(keyword_hits) / len(jd_skill_names) if jd_skill_names else raw_overlap
    # Blend skill match (70%) + raw token overlap (30%)
    keyword_score = int(min(100, (skill_match_ratio * 0.7 + raw_overlap * 0.3) * 100))

    if keyword_score < 60:
        missing_display = ", ".join(keyword_misses[:5])
        tips.append(f"Add missing keywords from the JD: {missing_display}.")
    elif keyword_score < 80:
        tips.append("Increase keyword density — mirror exact phrasing from the job description.")

    # ── 2. Format & Structure (20%) ───────────────────────────────────────────
    format_score = 100
    format_issues: list[str] = []

    # Check for bad patterns
    for pat in _BAD_PATTERNS:
        if re.search(pat, resume_text, re.IGNORECASE):
            format_score -= 20
            format_issues.append("Remove tables, images, or special characters — ATS cannot parse them.")
            break

    # Length check: 400–1200 words is ideal
    word_count = len(resume_text.split())
    if word_count < 200:
        format_score -= 25
        format_issues.append(f"Resume is too short ({word_count} words). Aim for 400–800 words.")
    elif word_count < 400:
        format_score -= 10
        format_issues.append(f"Resume is brief ({word_count} words). Consider expanding experience details.")
    elif word_count > 1500:
        format_score -= 15
        format_issues.append(f"Resume is long ({word_count} words). Keep to 1–2 pages (400–800 words).")

    # Check for contact info signals
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'(\+?\d[\d\s\-().]{7,}\d)', resume_text))
    if not has_email:
        format_score -= 10
        format_issues.append("Add your email address — ATS systems require contact information.")
    if not has_phone:
        format_score -= 5
        format_issues.append("Add a phone number for complete contact information.")

    format_score = max(0, format_score)
    tips.extend(format_issues[:2])  # top 2 format tips

    # ── 3. Section Coverage (20%) ─────────────────────────────────────────────
    sections_found: list[str] = []
    sections_missing: list[str] = []

    for section, pattern in _SECTION_PATTERNS.items():
        if re.search(pattern, resume_lower):
            sections_found.append(section)
        else:
            sections_missing.append(section)

    # Weight: experience + skills + education are critical
    critical = {"experience", "skills", "education"}
    critical_found = critical & set(sections_found)
    critical_score = len(critical_found) / len(critical)
    bonus_score = len(sections_found) / len(_SECTION_PATTERNS)
    section_score = int((critical_score * 0.7 + bonus_score * 0.3) * 100)

    if "experience" not in sections_found:
        tips.append("Add a clearly labeled 'Experience' or 'Work History' section.")
    if "skills" not in sections_found:
        tips.append("Add a dedicated 'Skills' or 'Technical Skills' section.")
    if "summary" not in sections_found:
        tips.append("Add a 'Summary' or 'Profile' section at the top — ATS ranks it highly.")

    # ── 4. Quantification (15%) ───────────────────────────────────────────────
    quant_matches = 0
    for pat in _QUANT_PATTERNS:
        quant_matches += len(re.findall(pat, resume_lower))

    # Ideal: 5+ quantified achievements
    quant_score = min(100, int((quant_matches / 5) * 100))

    if quant_score < 40:
        tips.append("Add metrics and numbers: 'Improved performance by 40%', 'Led team of 8', 'Reduced latency by 200ms'.")
    elif quant_score < 70:
        tips.append("Add more quantified achievements — numbers make your impact concrete and ATS-friendly.")

    # ── 5. Action Verbs (10%) ─────────────────────────────────────────────────
    # Count bullet-like lines starting with action verbs
    lines = resume_text.split('\n')
    bullet_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) > 20]
    action_verb_lines = 0

    for line in bullet_lines:
        first_word = re.match(r'^[•\-\*]?\s*(\w+)', line)
        if first_word and first_word.group(1).lower() in _ACTION_VERBS:
            action_verb_lines += 1

    # Ideal: 60%+ of bullet lines start with action verbs
    if bullet_lines:
        action_ratio = action_verb_lines / len(bullet_lines)
        action_score = min(100, int(action_ratio * 150))  # 67% ratio = 100
    else:
        action_score = 30

    if action_score < 50:
        tips.append("Start bullet points with strong action verbs: 'Built', 'Optimized', 'Led', 'Deployed', 'Reduced'.")

    # ── Weighted overall score ────────────────────────────────────────────────
    ats_score = int(
        keyword_score   * 0.35 +
        format_score    * 0.20 +
        section_score   * 0.20 +
        quant_score     * 0.15 +
        action_score    * 0.10
    )
    ats_score = max(0, min(100, ats_score))

    # ── Grade label ───────────────────────────────────────────────────────────
    if ats_score >= 85:
        grade = "EXCELLENT"
    elif ats_score >= 70:
        grade = "GOOD"
    elif ats_score >= 55:
        grade = "FAIR"
    else:
        grade = "NEEDS WORK"

    # Deduplicate tips, cap at 5
    seen_tips: set[str] = set()
    unique_tips: list[str] = []
    for t in tips:
        if t not in seen_tips:
            seen_tips.add(t)
            unique_tips.append(t)
        if len(unique_tips) == 5:
            break

    return {
        "ats_score": ats_score,
        "ats_grade": grade,
        "dimensions": {
            "keyword_match": keyword_score,
            "format_structure": format_score,
            "section_coverage": section_score,
            "quantification": quant_score,
            "action_verbs": action_score,
        },
        "tips": unique_tips,
        "keyword_hits": keyword_hits[:10],
        "keyword_misses": keyword_misses[:10],
        "sections_found": sections_found,
        "sections_missing": sections_missing,
    }
