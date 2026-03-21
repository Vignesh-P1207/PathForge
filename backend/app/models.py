"""Pydantic schemas — PathForge API."""

from typing import List, Literal, Optional
from pydantic import BaseModel


class SkillItem(BaseModel):
    name: str
    pct: int
    type: Literal["match", "gap", "req"]


class TraceItem(BaseModel):
    tag: str
    msg: str


class PathwayItem(BaseModel):
    week: str
    title: str
    desc: str
    tag: str
    tagLabel: str
    hrs: str
    mods: str


class AtsDimensions(BaseModel):
    keyword_match: int
    format_structure: int
    section_coverage: int
    quantification: int
    action_verbs: int


class AtsResult(BaseModel):
    ats_score: int
    ats_grade: str
    dimensions: AtsDimensions
    tips: List[str]
    keyword_hits: List[str]
    keyword_misses: List[str]
    sections_found: List[str]
    sections_missing: List[str]


class AnalysisResponse(BaseModel):
    match_pct: int
    critical_gaps: int
    time_saved_pct: int
    current_skills: List[SkillItem]
    required_skills: List[SkillItem]
    reasoning_trace: List[TraceItem]
    pathway: List[PathwayItem]
    weeks_to_ready: int
    ats: AtsResult
    jd_company: Optional[str] = None
    interview_readiness: Optional["InterviewReadinessResponse"] = None


# ── Bulk Analyzer ─────────────────────────────────────────────────────────────

class CandidateResult(BaseModel):
    rank: int
    candidate: str
    filename: str
    match_pct: int
    time_saved_pct: int
    matched_count: int
    gap_count: int
    top_skills: List[str]
    critical_gaps: List[str]
    is_top: bool


class BulkAnalysisResponse(BaseModel):
    total_candidates: int
    job_description_skills: int
    top_candidates: List[CandidateResult]
    all_candidates: List[CandidateResult]
    avg_match_pct: int
    best_match_pct: int
    common_gaps: List[str]
    jd_company: Optional[str] = None


# ── Standalone ATS Scanner ────────────────────────────────────────────────────

class ATSIssue(BaseModel):
    type: str
    severity: Literal["high", "medium", "low"]
    message: str


class ATSScanResponse(BaseModel):
    ats_score: int
    keyword_score: int
    section_score: int
    formatting_score: int
    present_keywords: List[str]
    missing_keywords: List[str]
    formatting_issues: List[ATSIssue]
    found_sections: List[str]
    suggestions: List[str]
    verdict: str
    jd_company: Optional[str] = None


# ── Interview Readiness ───────────────────────────────────────────────────────

class DangerZone(BaseModel):
    skill: str
    severity: Literal["high", "medium", "low"]
    questions: List[str]
    prep_strategy: str


class StrongZone(BaseModel):
    skill: str
    proficiency: int
    questions: List[str]


class InterviewReadinessResponse(BaseModel):
    level: Literal["low", "medium", "high"]
    label: str
    confidence: int
    prep_days: int
    danger_zones: List[DangerZone]
    strong_zones: List[StrongZone]
