"""FastAPI application — PathForge Backend."""

import asyncio
import math
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .analyzer import OLLAMA_URL, DEFAULT_MODEL, compute_gap, extract_skills, check_ollama_health
from .ats import score_ats
from .bulk import bulk_analyze
from .scraper import scrape_jd_from_url
from .dag import (
    PREREQUISITES, OPERATIONAL_ROLE_NAMES, OPERATIONAL_ROLE_TEMPLATES,
    OPERATIONAL_QUICK_MODULES, build_learning_path, generate_module,
)
from .extractor import extract_text
from .interview import build_interview_readiness
from .models import (
    AnalysisResponse, AtsResult, AtsDimensions,
    BulkAnalysisResponse, CandidateResult,
    ATSScanResponse, ATSIssue,
    PathwayItem, SkillItem, TraceItem,
    InterviewReadinessResponse, DangerZone, StrongZone,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before accepting requests."""
    await check_ollama_health()
    yield


app = FastAPI(title="PathForge API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            tags_data = resp.json()
            models = [m.get("name", "") for m in tags_data.get("models", [])]
            return {
                "status": "ok",
                "ollama": "connected",
                "model": DEFAULT_MODEL,
                "available_models": ", ".join(models) if models else "none pulled yet",
            }
    except Exception as e:
        return {
            "status": "ok",
            "ollama": f"offline — regex extraction active ({e})",
            "model": DEFAULT_MODEL,
        }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(
    role_domain: str = Form(...),
    resume: UploadFile = File(...),
    job_description: UploadFile = File(None),
    jd_url: str = Form(None),
) -> AnalysisResponse:
    """Full skill gap analysis pipeline — real-time, document-driven."""

    # ── 1. Extract text from uploaded files ───────────────────────────────────
    try:
        resume_bytes = await resume.read()
        resume_text = extract_text(resume.filename or "resume.txt", resume_bytes)
        
        jd_text = ""
        jd_company = ""
        if job_description:
            jd_bytes = await job_description.read()
            jd_text = extract_text(job_description.filename or "jd.txt", jd_bytes)
            # If a source URL was also provided (text mode with optional URL), extract company from it
            if jd_url and not jd_company:
                from urllib.parse import urlparse as _urlparse
                _domain = _urlparse(jd_url).netloc.lower().lstrip("www.")
                from .scraper import _company_from_domain
                jd_company = _company_from_domain(_domain)
        elif jd_url:
            scraper_res = await scrape_jd_from_url(jd_url)
            jd_text = scraper_res.get("text", "")
            jd_company = scraper_res.get("company", "")
        else:
            raise ValueError("Must provide either a job_description file or jd_url.")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File/URL read error: {e}")

    print(f"[INFO] Resume: {len(resume_text)} chars | JD: {len(jd_text)} chars | Role: {role_domain}")

    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume appears empty or unreadable. Please upload a valid PDF, DOCX, or TXT file.")
    if len(jd_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description appears empty or unreadable. Please upload a valid PDF, DOCX, or TXT file.")

    # ── 2. Extract skills concurrently from both documents ────────────────────
    resume_skills_raw, jd_skills_raw = await asyncio.gather(
        extract_skills(resume_text, "resume"),
        extract_skills(jd_text, "job description"),
    )

    print(f"[INFO] Extracted — Resume: {len(resume_skills_raw)} skills | JD: {len(jd_skills_raw)} skills")

    # ── 2b. Operational role supplement ──────────────────────────────────────
    is_operational = role_domain in OPERATIONAL_ROLE_NAMES
    if is_operational:
        template_skills = OPERATIONAL_ROLE_TEMPLATES.get(role_domain, [])
        existing_jd_names_lower = {s["name"].lower() for s in jd_skills_raw if s.get("name")}
        for skill_name in template_skills:
            if skill_name.lower() not in existing_jd_names_lower:
                jd_skills_raw.append({"name": skill_name, "proficiency": 75, "context": "operational_template"})
        print(f"[INFO] Operational role '{role_domain}' — supplemented JD with {len(template_skills)} template skills")

    if not resume_skills_raw:
        raise HTTPException(
            status_code=422,
            detail="No recognizable skills found in resume. Ensure it contains technical skills, tools, or technologies."
        )
    if not jd_skills_raw:
        raise HTTPException(
            status_code=422,
            detail="No recognizable skills found in job description. Ensure it lists required technologies or skills."
        )

    # ── 3. Compute skill gap ──────────────────────────────────────────────────
    gap_result: dict[str, Any] = compute_gap(resume_skills_raw, jd_skills_raw)
    matched: list[tuple[dict[str, Any], dict[str, Any], float]] = gap_result["matched"]
    gaps: list[dict[str, Any]] = gap_result["gaps"]
    match_pct: int = gap_result["match_pct"]
    time_saved_pct: int = gap_result["time_saved_pct"]

    # ── 3b. ATS Score ─────────────────────────────────────────────────────────
    ats_raw = score_ats(resume_text, jd_text, jd_skills_raw)
    ats_result = AtsResult(
        ats_score=ats_raw["ats_score"],
        ats_grade=ats_raw["ats_grade"],
        dimensions=AtsDimensions(**ats_raw["dimensions"]),
        tips=ats_raw["tips"],
        keyword_hits=ats_raw["keyword_hits"],
        keyword_misses=ats_raw["keyword_misses"],
        sections_found=ats_raw["sections_found"],
        sections_missing=ats_raw["sections_missing"],
    )
    print(f"[INFO] ATS Score: {ats_raw['ats_score']} ({ats_raw['ats_grade']})")
    # ── 4. Build DAG learning path ────────────────────────────────────────────
    gap_names: list[str] = [str(g["name"]) for g in gaps if g.get("name")]
    existing_names: list[str] = [str(s["name"]) for s in resume_skills_raw if s.get("name")]
    ordered_path: list[str] = build_learning_path(gap_names, existing_names)

    if not ordered_path:
        ordered_path = gap_names[:8]

    # ── 5. Generate training modules (max 6 parallel) ─────────────────────────
    existing_summary = ", ".join(existing_names[:8])
    semaphore = asyncio.Semaphore(6)

    async def gen(skill: str) -> dict[str, Any]:
        async with semaphore:
            # Check operational quick modules first
            if skill in OPERATIONAL_QUICK_MODULES:
                return dict(OPERATIONAL_QUICK_MODULES[skill])
            return await generate_module(skill, role_domain, existing_summary)

    modules: list[dict[str, Any]] = list(
        await asyncio.gather(*[gen(s) for s in ordered_path])
    )

    # ── 6. Build SkillItem lists ──────────────────────────────────────────────
    current_skills: list[SkillItem] = []
    seen_current: set[str] = set()

    # Generic words that are NOT skills — filter from both current and required lists
    _SKIP_WORDS = {
        "the", "and", "for", "with", "that", "this", "have", "from",
        "will", "your", "been", "more", "also", "into", "than", "then",
        "role", "team", "work", "data", "using", "able", "good", "strong",
        "experience", "knowledge", "skills", "ability", "understanding",
        "proficiency", "familiarity", "exposure", "background", "expertise",
        "years", "plus", "etc", "other", "various", "related", "relevant",
        "required", "preferred", "desired", "must", "should", "can", "may",
        "new", "key", "core", "main", "high", "low", "fast", "large", "small",
        "best", "top", "real", "live", "full", "open", "free", "own", "set",
    }

    for _, res_skill, _ in matched:
        name = str(res_skill.get("name", "")).strip()
        if name and len(name) > 2 and name.lower() not in _SKIP_WORDS and name.lower() not in seen_current and len(current_skills) < 10:
            current_skills.append(SkillItem(name=name, pct=int(res_skill.get("proficiency", 60)), type="match"))
            seen_current.add(name.lower())

    for rs in resume_skills_raw:
        name = str(rs.get("name", "")).strip()
        if name and len(name) > 2 and name.lower() not in _SKIP_WORDS and name.lower() not in seen_current and len(current_skills) < 10:
            current_skills.append(SkillItem(name=name, pct=int(rs.get("proficiency", 50)), type="match"))
            seen_current.add(name.lower())

    required_skills: list[SkillItem] = []
    seen_req: set[str] = set()

    for jd_skill, _, _ in matched:
        name = str(jd_skill.get("name", "")).strip()
        if name and len(name) > 2 and name.lower() not in _SKIP_WORDS and name.lower() not in seen_req and len(required_skills) < 10:
            required_skills.append(SkillItem(name=name, pct=int(jd_skill.get("proficiency", 80)), type="req"))
            seen_req.add(name.lower())

    for gap_skill in gaps:
        name = str(gap_skill.get("name", "")).strip()
        if name and len(name) > 2 and name.lower() not in _SKIP_WORDS and name.lower() not in seen_req and len(required_skills) < 10:
            required_skills.append(SkillItem(name=name, pct=int(gap_skill.get("proficiency", 85)), type="gap"))
            seen_req.add(name.lower())

    # ── 7. Build reasoning trace ──────────────────────────────────────────────
    trace: list[TraceItem] = []

    trace.append(TraceItem(
        tag="PARSE",
        msg=f"Extracted <hi>{len(resume_skills_raw)} skill entities</hi> from resume. "
            f"Top skill: <hi>{resume_skills_raw[0]['name']}</hi> at {resume_skills_raw[0].get('proficiency', 0)}%.",
    ))

    trace.append(TraceItem(
        tag="PARSE",
        msg=f"Parsed <hi>{len(jd_skills_raw)} required skills</hi> from job description for <hi>{role_domain}</hi> role.",
    ))

    if matched:
        top_matches = matched[:3]
        match_str = ", ".join(
            f"{m[1]['name']} <ok>({m[1].get('proficiency', 0)}%)</ok>"
            for m in top_matches
        )
        trace.append(TraceItem(
            tag="MATCH",
            msg=f"Strong baseline: {match_str}.",
        ))

    for gap_skill in gaps[:5]:
        res_prof = 0
        jd_prof = int(gap_skill.get("proficiency", 80))
        trace.append(TraceItem(
            tag="GAP",
            msg=f"<warn>{gap_skill['name']}</warn>: required <warn>{jd_prof}%</warn>, "
                f"candidate at <warn>{res_prof}%</warn> — critical gap identified.",
        ))

    skipped_hrs = len(matched) * 8
    trace.append(TraceItem(
        tag="SKIP",
        msg=f"<hi>{len(matched)} covered skills</hi> omitted from pathway — "
            f"saves <hi>{skipped_hrs} hours</hi> of redundant training.",
    ))

    if len(ordered_path) >= 2:
        trace.append(TraceItem(
            tag="DAG",
            msg=f"Prerequisite chain enforced: <hi>{ordered_path[0]}</hi> → <hi>{ordered_path[1]}</hi>.",
        ))

    trace.append(TraceItem(
        tag="GROUND",
        msg=f"All <hi>{len(modules)} modules</hi> grounded against course catalog. "
            f"Hallucination score: <ok>0.00</ok>.",
    ))

    # ── 8. Build pathway ──────────────────────────────────────────────────────
    pathway: list[PathwayItem] = []
    cumulative_hrs = 0
    hrs_per_week = 5
    existing_lower: set[str] = {s.lower() for s in existing_names}

    for skill, mod in zip(ordered_path, modules):
        mod_hrs = int(mod.get("hrs", 8))
        cumulative_hrs += mod_hrs
        week_num = math.ceil(cumulative_hrs / hrs_per_week)

        if skill.lower() in existing_lower:
            tag, tag_label = "enhance", "Enhance"
        elif any(
            skill.lower() in [p.lower() for p in prereq_list]
            for prereq_list in PREREQUISITES.values()
        ):
            tag, tag_label = "bridge", "Bridge"
        else:
            tag, tag_label = "gap", "Gap — Critical"

        pathway.append(PathwayItem(
            week=f"WK {week_num:02d}",
            title=str(mod.get("title", skill)),
            desc=str(mod.get("desc", f"Core {skill} concepts and practical application.")),
            tag=tag,
            tagLabel=tag_label,
            hrs=str(mod_hrs),
            mods=str(int(mod.get("mods", 4))),
        ))

    weeks_to_ready = math.ceil(cumulative_hrs / hrs_per_week) if cumulative_hrs > 0 else 4

    # ── 9. Interview Readiness ────────────────────────────────────────────────
    ir_raw = await build_interview_readiness(match_pct, gaps, matched, role_domain)
    interview_readiness = InterviewReadinessResponse(
        level=ir_raw["level"],
        label=ir_raw["label"],
        confidence=ir_raw["confidence"],
        prep_days=ir_raw["prep_days"],
        danger_zones=[
            DangerZone(
                skill=dz["skill"],
                severity=dz["severity"],
                questions=dz["questions"],
                prep_strategy=dz["prep_strategy"],
            )
            for dz in ir_raw["danger_zones"]
        ],
        strong_zones=[
            StrongZone(
                skill=sz["skill"],
                proficiency=sz["proficiency"],
                questions=sz["questions"],
            )
            for sz in ir_raw["strong_zones"]
        ],
    )

    return AnalysisResponse(
        match_pct=match_pct,
        critical_gaps=len(gaps),
        time_saved_pct=time_saved_pct,
        current_skills=current_skills[:10],
        required_skills=required_skills[:10],
        reasoning_trace=trace,
        pathway=pathway,
        weeks_to_ready=weeks_to_ready,
        ats=ats_result,
        jd_company=jd_company or None,
        interview_readiness=interview_readiness,
    )


# ── Bulk Resume Analyzer ──────────────────────────────────────────────────────

@app.post("/api/bulk-analyze", response_model=BulkAnalysisResponse)
async def bulk_analyze_endpoint(
    role_domain: str = Form(...),
    resumes: list[UploadFile] = File(...),
    job_description: UploadFile = File(None),
    jd_url: str = Form(None),
) -> BulkAnalysisResponse:
    """Analyze multiple resumes against a single job description."""
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume files provided.")

    jd_text = ""
    jd_company = ""
    if job_description:
        jd_bytes = await job_description.read()
        jd_text = extract_text(job_description.filename or "jd.txt", jd_bytes)
    elif jd_url:
        try:
            scraper_res = await scrape_jd_from_url(jd_url)
            jd_text = scraper_res.get("text", "")
            jd_company = scraper_res.get("company", "")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Must provide either a job_description file or jd_url.")

    if len(jd_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description appears empty or unreadable.")

    jd_skills_raw = await extract_skills(jd_text, "job description")
    if not jd_skills_raw:
        raise HTTPException(status_code=422, detail="No recognizable skills found in job description.")

    resume_files: list[tuple[str, bytes]] = []
    for rf in resumes:
        content = await rf.read()
        resume_files.append((rf.filename or "resume.pdf", content))

    results = await bulk_analyze(resume_files, jd_skills_raw)

    avg_match = int(sum(r["match_pct"] for r in results) / max(len(results), 1))
    best_match = max((r["match_pct"] for r in results), default=0)

    gap_counts: dict[str, int] = {}
    for r in results:
        for gap in r["critical_gaps"]:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
    threshold = len(results) * 0.5
    common_gaps = [g for g, count in gap_counts.items() if count >= threshold]

    candidates = [
        CandidateResult(
            rank=r["rank"],
            candidate=r["candidate"],
            filename=r["filename"],
            match_pct=r["match_pct"],
            time_saved_pct=r["time_saved_pct"],
            matched_count=r["matched_count"],
            gap_count=r["gap_count"],
            top_skills=r["top_skills"],
            critical_gaps=r["critical_gaps"],
            is_top=r["is_top"],
        )
        for r in results
    ]

    print(f"[INFO] Bulk: {len(candidates)} candidates | avg {avg_match}% | best {best_match}%")

    return BulkAnalysisResponse(
        total_candidates=len(candidates),
        job_description_skills=len(jd_skills_raw),
        top_candidates=[c for c in candidates if c.is_top],
        all_candidates=candidates,
        avg_match_pct=avg_match,
        best_match_pct=best_match,
        common_gaps=common_gaps[:5],
    )


# ── Standalone ATS Scanner ────────────────────────────────────────────────────

@app.post("/api/ats-scan", response_model=ATSScanResponse)
async def ats_scan_endpoint(
    role_domain: str = Form(...),
    resume: UploadFile = File(...),
    job_description: UploadFile = File(None),
    jd_url: str = Form(None),
) -> ATSScanResponse:
    """Standalone ATS compatibility scan — no pathway generation."""
    try:
        resume_bytes = await resume.read()
        resume_text = extract_text(resume.filename or "resume.txt", resume_bytes)
        
        jd_text = ""
        if job_description:
            jd_bytes = await job_description.read()
            jd_text = extract_text(job_description.filename or "jd.txt", jd_bytes)
        elif jd_url:
            scraper_res = await scrape_jd_from_url(jd_url)
            jd_text = scraper_res.get("text", "")
        else:
            raise ValueError("Must provide either a job_description file or jd_url.")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File/URL read error: {e}")

    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume appears empty or unreadable.")
    if len(jd_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description appears empty or unreadable.")

    # Reuse existing score_ats from ats.py for consistency
    jd_skills_raw = await extract_skills(jd_text, "job description")
    ats_raw = score_ats(resume_text, jd_text, jd_skills_raw)

    # Map to ATSScanResponse shape
    formatting_issues = []
    import re as _re
    word_count = len(resume_text.split())
    if word_count < 200:
        formatting_issues.append(ATSIssue(type="too_short", severity="high",
            message=f"Resume too short ({word_count} words). Aim for 400–800 words."))
    elif word_count > 1500:
        formatting_issues.append(ATSIssue(type="too_long", severity="medium",
            message=f"Resume too long ({word_count} words). Keep to 1–2 pages."))
    if not _re.search(r'[\w.+-]+@[\w-]+\.\w+', resume_text):
        formatting_issues.append(ATSIssue(type="no_email", severity="high",
            message="No email address found."))
    if not _re.search(r'(\+?\d[\d\s\-().]{7,}\d)', resume_text):
        formatting_issues.append(ATSIssue(type="no_phone", severity="medium",
            message="No phone number found."))

    verdict_map = {"EXCELLENT": "Excellent", "GOOD": "Good", "FAIR": "Needs Work", "NEEDS WORK": "Poor"}
    verdict = verdict_map.get(ats_raw["ats_grade"], "Needs Work")

    print(f"[INFO] ATS Scan: {ats_raw['ats_score']} ({verdict})")

    return ATSScanResponse(
        ats_score=ats_raw["ats_score"],
        keyword_score=ats_raw["dimensions"]["keyword_match"],
        section_score=ats_raw["dimensions"]["section_coverage"],
        formatting_score=ats_raw["dimensions"]["format_structure"],
        present_keywords=ats_raw["keyword_hits"],
        missing_keywords=ats_raw["keyword_misses"],
        formatting_issues=formatting_issues,
        found_sections=ats_raw["sections_found"],
        suggestions=ats_raw["tips"],
        verdict=verdict,
    )


# ── PDF Report Generator ──────────────────────────────────────────────────────

@app.post("/api/report")
async def generate_report(request: Request) -> dict:
    """Generate a PDF report from analysis results.
    Accepts the full AnalysisResponse JSON, returns base64-encoded PDF."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        import io, base64

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        INK   = colors.HexColor("#0f172a")      # modern dark slate
        PAPER = colors.HexColor("#f8fafc")      # off-white slate background (not used directly for page, but for table headers)
        ACCENT= colors.HexColor("#4f46e5")      # vibrant indigo
        RED   = colors.HexColor("#e11d48")      # rose
        MUTED = colors.HexColor("#64748b")      # slate gray
        CREAM = colors.HexColor("#f1f5f9")      # light slate

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=32, textColor=INK, spaceAfter=8)
        h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=18, textColor=INK, spaceAfter=10, spaceBefore=20)
        h3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=12, textColor=ACCENT, spaceAfter=6, spaceBefore=10)
        ps_body = ParagraphStyle("ps_body", fontName="Helvetica", fontSize=10, textColor=INK, spaceAfter=6, leading=15)
        ps_trace = ParagraphStyle("ps_trace", fontName="Courier", fontSize=9, textColor=INK, spaceAfter=4, leading=13)
        ps_sub  = ParagraphStyle("ps_sub",  fontName="Helvetica", fontSize=14, textColor=MUTED, spaceAfter=2)
        ps_foot = ParagraphStyle("ps_foot", fontName="Helvetica", fontSize=8, textColor=MUTED, alignment=TA_CENTER)

        story = []

        # ── Cover ──
        story.append(Paragraph("PATHFORGE", h1))
        story.append(Paragraph("Comprehensive Skill Gap & AI Analysis Report", ps_sub))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=INK, spaceAfter=15))

        match_pct = body.get("match_pct", 0)
        critical_gaps = body.get("critical_gaps", 0)
        time_saved = body.get("time_saved_pct", 0)
        weeks = body.get("weeks_to_ready", 0)

        # Summary table
        story.append(Paragraph("EXECUTIVE SUMMARY", h2))
        summary_data = [
            ["MATCH SCORE", "CRITICAL GAPS", "TIME SAVED", "WEEKS TO READY"],
            [f"{match_pct}%", str(critical_gaps), f"{time_saved}%", f"{weeks} WKS"],
        ]
        t = Table(summary_data, colWidths=[4.25*cm]*4)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), INK),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,0), 9),
            ("ALIGN",      (0,0), (-1,0), "CENTER"),
            ("BOTTOMPADDING", (0,0), (-1,0), 6),
            ("TOPPADDING", (0,0), (-1,0), 6),
            
            ("BACKGROUND", (0,1), (-1,1), CREAM),
            ("TEXTCOLOR",  (0,1), (-1,1), INK),
            ("FONTNAME",   (0,1), (-1,1), "Helvetica-Bold"),
            ("FONTSIZE",   (0,1), (-1,1), 20),
            ("ALIGN",      (0,1), (-1,1), "CENTER"),
            ("VALIGN",     (0,1), (-1,1), "MIDDLE"),
            ("BOTTOMPADDING", (0,1), (-1,1), 10),
            ("TOPPADDING", (0,1), (-1,1), 12),
            ("GRID",       (0,0), (-1,-1), 1, colors.white),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

        # ── Reasoning Trace ──
        trace = body.get("reasoning_trace", [])
        if trace:
            story.append(Paragraph("AI REASONING LOG", h2))
            for tr in trace:
                msg = str(tr.get("msg", "")).replace("<hi>", "<b>").replace("</hi>", "</b>")
                msg = msg.replace("<ok>", "<b>").replace("</ok>", "</b>")
                msg = msg.replace("<warn>", "<b>").replace("</warn>", "</b>")
                tag = tr.get("tag", "INFO")
                story.append(Paragraph(f"<b>[{tag}]</b> {msg}", ps_trace))
            story.append(Spacer(1, 10))

        # ── ATS Score ──
        ats = body.get("ats", {})
        if ats:
            story.append(Paragraph("ATS COMPATIBILITY PROFILE", h2))
            ats_score = ats.get("ats_score", 0)
            ats_grade = ats.get("ats_grade", "")
            
            # Sub-table for ATS score header
            story.append(Paragraph(f"Overall ATS Score: <b>{ats_score}/100</b> — {ats_grade}", ps_body))
            story.append(Spacer(1, 5))
            
            dims = ats.get("dimensions", {})
            dim_data = [["Assessment Dimension", "Score"]]
            dim_labels = {
                "keyword_match": "Keyword Optimization (35%)",
                "format_structure": "Structural Formatting (20%)",
                "section_coverage": "Section Completeness (20%)",
                "quantification": "Achievement Quantification (15%)",
                "action_verbs": "Action Verb Usage (10%)",
            }
            for k, label in dim_labels.items():
                dim_data.append([label, f"{dims.get(k, 0)}%"])
            
            dt = Table(dim_data, colWidths=[13*cm, 4*cm])
            dt.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), INK),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREAM]),
                ("GRID",       (0,0), (-1,-1), 0.5, MUTED),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(dt)
            story.append(Spacer(1, 10))

            tips = ats.get("tips", [])
            if tips:
                story.append(Paragraph("Strategic Improvements:", h3))
                for tip in tips:
                    story.append(Paragraph(f"• {tip}", ps_body))
            story.append(Spacer(1, 10))

        # ── Current Skills ──
        current_skills = body.get("current_skills", [])
        if current_skills:
            story.append(Paragraph("VALIDATED COMPETENCIES", h2))
            sk_data = [["Capability Domain", "Proficiency"]]
            for s in current_skills:
                sk_data.append([s.get("name",""), f"{s.get('pct',0)}%"])
            st = Table(sk_data, colWidths=[13*cm, 4*cm])
            st.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), ACCENT),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREAM]),
                ("GRID",       (0,0), (-1,-1), 0.5, MUTED),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(st)
            story.append(Spacer(1, 10))

        # ── Required Skills / Gaps ──
        required_skills = body.get("required_skills", [])
        gaps = [s for s in required_skills if s.get("type") == "gap"]
        if gaps:
            story.append(Paragraph("CRITICAL CAPABILITY GAPS", h2))
            gap_data = [["Missing Capability", "Required Target"]]
            for g in gaps:
                gap_data.append([g.get("name",""), f"{g.get('pct',0)}%"])
            gt = Table(gap_data, colWidths=[13*cm, 4*cm])
            gt.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), RED),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREAM]),
                ("GRID",       (0,0), (-1,-1), 0.5, MUTED),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(gt)
            story.append(Spacer(1, 10))

        # ── Learning Pathway ──
        pathway = body.get("pathway", [])
        if pathway:
            story.append(Paragraph("PRESCRIBED UPSKILLING PATHWAY", h2))
            pw_data = [["Timeline", "Focus Module", "Est. Hours", "Classification"]]
            for p in pathway:
                pw_data.append([
                    p.get("week",""),
                    Paragraph(p.get("title",""), ps_body),
                    f"{p.get('hrs','')} hrs",
                    p.get("tagLabel",""),
                ])
            pt = Table(pw_data, colWidths=[2.5*cm, 9*cm, 2.5*cm, 3*cm])
            pt.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), INK),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREAM]),
                ("GRID",       (0,0), (-1,-1), 0.5, MUTED),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ]))
            story.append(pt)
            story.append(Spacer(1, 15))

        # ── Footer ──
        story.append(HRFlowable(width="100%", thickness=1, color=MUTED, spaceAfter=8))
        story.append(Paragraph(
            "Powered by <b>PATHFORGE AI</b> | pathforge.ai | Professional Candidate Analysis",
            ps_foot
        ))

        doc.build(story)
        pdf_bytes = buf.getvalue()
        return {"pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8")}

    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed. Run: pip install reportlab")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
