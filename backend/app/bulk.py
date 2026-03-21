"""Bulk Resume Analyzer — PathForge Backend.

Analyzes multiple resumes concurrently against a single job description,
ranks candidates by match percentage, and surfaces common skill gaps.
"""

from typing import Any
import asyncio

from .analyzer import extract_skills, compute_gap
from .extractor import extract_text


async def analyze_single_resume(
    filename: str,
    file_bytes: bytes,
    jd_skills: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyze one resume against pre-extracted JD skills."""
    try:
        text = extract_text(filename, file_bytes)
    except Exception as e:
        return {
            "candidate": filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title(),
            "filename": filename,
            "match_pct": 0,
            "time_saved_pct": 0,
            "matched_count": 0,
            "gap_count": 0,
            "top_skills": [],
            "critical_gaps": [],
            "resume_skills": [],
            "error": str(e),
        }

    candidate_name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    resume_skills = await extract_skills(text, "resume")
    gap_result = compute_gap(resume_skills, jd_skills)

    return {
        "candidate": candidate_name,
        "filename": filename,
        "match_pct": gap_result["match_pct"],
        "time_saved_pct": gap_result["time_saved_pct"],
        "matched_count": len(gap_result["matched"]),
        "gap_count": len(gap_result["gaps"]),
        "top_skills": [str(s.get("name", "")) for s in resume_skills[:4]],
        "critical_gaps": [str(g.get("name", "")) for g in gap_result["gaps"][:3]],
        "resume_skills": resume_skills,
    }


async def bulk_analyze(
    resume_files: list[tuple[str, bytes]],
    jd_skills: list[dict[str, Any]],
    max_parallel: int = 5,
) -> list[dict[str, Any]]:
    """Analyze multiple resumes concurrently against JD skills."""
    semaphore = asyncio.Semaphore(max_parallel)

    async def analyze_with_sem(filename: str, file_bytes: bytes) -> dict[str, Any]:
        async with semaphore:
            return await analyze_single_resume(filename, file_bytes, jd_skills)

    results = list(await asyncio.gather(*[
        analyze_with_sem(fn, fb) for fn, fb in resume_files
    ]))

    # Sort by match_pct descending
    sorted_results = sorted(results, key=lambda x: x["match_pct"], reverse=True)

    for i, r in enumerate(sorted_results):
        r["rank"] = i + 1
        r["is_top"] = i < 3

    return sorted_results
