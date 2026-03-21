"""URL-based Job Description Scraper — PathForge Backend.

Supports: LinkedIn, Indeed, Naukri, Glassdoor, Internshala,
          Wellfound (AngelList), Greenhouse, Lever, Workday,
          Monster, SimplyHired, ZipRecruiter, and generic JSON-LD.

Strategy order per site:
  1. Site-specific selectors / API
  2. JSON-LD schema.org/JobPosting
  3. Full-page text extraction
"""

import json
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ── Browser-like headers ──────────────────────────────────────────────────────
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


# ── Company name from domain ──────────────────────────────────────────────────
_DOMAIN_COMPANY_MAP = {
    "linkedin.com": "LinkedIn",
    "indeed.com": "Indeed",
    "naukri.com": "Naukri",
    "glassdoor.com": "Glassdoor",
    "internshala.com": "Internshala",
    "wellfound.com": "Wellfound",
    "angel.co": "AngelList",
    "monster.com": "Monster",
    "simplyhired.com": "SimplyHired",
    "ziprecruiter.com": "ZipRecruiter",
    "greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
    "workday.com": "Workday",
    "smartrecruiters.com": "SmartRecruiters",
    "jobvite.com": "Jobvite",
    "icims.com": "iCIMS",
    "taleo.net": "Taleo",
    "myworkdayjobs.com": "Workday",
    "careers.google.com": "Google",
    "amazon.jobs": "Amazon",
    "microsoft.com": "Microsoft",
    "apple.com": "Apple",
    "meta.com": "Meta",
    "jobs.netflix.com": "Netflix",
    "infosys.com": "Infosys",
    "wipro.com": "Wipro",
    "tcs.com": "TCS",
    "hcltech.com": "HCL Technologies",
    "accenture.com": "Accenture",
    "ibm.com": "IBM",
    "oracle.com": "Oracle",
    "sap.com": "SAP",
}


def _company_from_domain(domain: str) -> str:
    """Best-effort company name from domain."""
    domain = domain.lower().lstrip("www.")
    for key, name in _DOMAIN_COMPANY_MAP.items():
        if key in domain:
            return name
    # Fallback: capitalize the root domain
    parts = domain.split(".")
    if parts:
        return parts[0].replace("-", " ").title()
    return ""


# ── Main entry point ──────────────────────────────────────────────────────────

async def scrape_jd_from_url(url: str) -> dict[str, str]:
    """Fetch and extract job description text + company from a URL.

    Returns: {"text": str, "company": str}
    Raises ValueError with a user-friendly message on failure.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower().lstrip("www.")
    print(f"[SCRAPE] Fetching: {url} | domain: {domain}")

    # Always try to get company from domain as fallback
    portal_company = _company_from_domain(domain)

    # 1. Site-specific handler
    result = await _try_site_specific(url, domain)
    if result and len(result.get("text", "").strip()) >= 100:
        if not result.get("company"):
            result["company"] = portal_company
        print(f"[SCRAPE] Site-specific: {len(result['text'])} chars, company={result['company']}")
        return result

    # 2. Generic fetch + JSON-LD + full text
    result = await _generic_fetch(url, domain, portal_company)
    if result and len(result.get("text", "").strip()) >= 100:
        print(f"[SCRAPE] Generic fetch: {len(result['text'])} chars, company={result['company']}")
        return result

    raise ValueError(
        "Could not extract the job description from this URL.\n\n"
        "Most job sites (Indeed, Naukri, Glassdoor) block automated access.\n"
        "Please open the job link in your browser, copy the full description text, "
        "and use the 'Paste Text' option instead."
    )


# ── Site-specific handlers ────────────────────────────────────────────────────

async def _try_site_specific(url: str, domain: str) -> dict[str, str] | None:
    if "linkedin.com" in domain:
        return await _scrape_linkedin(url)
    if "indeed.com" in domain:
        return await _scrape_indeed(url)
    if "naukri.com" in domain:
        return await _scrape_naukri(url)
    if "glassdoor.com" in domain:
        return await _scrape_glassdoor(url)
    if "internshala.com" in domain:
        return await _scrape_internshala(url)
    if "wellfound.com" in domain or "angel.co" in domain:
        return await _scrape_wellfound(url)
    if "greenhouse.io" in domain:
        return await _scrape_greenhouse(url)
    if "lever.co" in domain:
        return await _scrape_lever(url)
    if "myworkdayjobs.com" in domain or "workday.com" in domain:
        return await _scrape_workday(url)
    if "monster.com" in domain:
        return await _scrape_monster(url)
    if "ziprecruiter.com" in domain:
        return await _scrape_ziprecruiter(url)
    return None


async def _fetch_html(url: str, extra_headers: dict | None = None, timeout: float = 15.0) -> tuple[int, str]:
    """Fetch URL and return (status_code, html_text)."""
    headers = {**_HEADERS, **(extra_headers or {})}
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(connect=8.0, read=timeout, write=5.0, pool=5.0),
        headers=headers,
    ) as client:
        resp = await client.get(url)
        return resp.status_code, resp.text


async def _scrape_linkedin(url: str) -> dict[str, str] | None:
    try:
        status, html = await _fetch_html(url)
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD first
        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        # Company name
        company = ""
        for sel in [
            ("a", {"class": re.compile(r"topcard__org-name-link", re.I)}),
            ("span", {"class": re.compile(r"topcard__flavor", re.I)}),
            ("a", {"class": re.compile(r"company-name", re.I)}),
        ]:
            el = soup.find(sel[0], sel[1])
            if el:
                company = el.get_text(strip=True)
                break

        # Description div
        for cls in [
            re.compile(r"description__text", re.I),
            re.compile(r"show-more-less-html", re.I),
            re.compile(r"job-description", re.I),
        ]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] LinkedIn failed: {e}")
        return None


async def _scrape_indeed(url: str) -> dict[str, str] | None:
    """Indeed blocks most bots. Try JSON-LD then specific divs."""
    try:
        # Indeed needs a Referer and cookie-like headers
        status, html = await _fetch_html(url, extra_headers={
            "Referer": "https://www.indeed.com/",
            "Cookie": "CTK=1; INDEED_CSRF_TOKEN=1",
        })
        if status == 403:
            print("[SCRAPE] Indeed returned 403 — bot protection active")
            return None
        if status != 200:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD
        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        # Company name
        company = ""
        for attr in [{"data-company-name": True}, {"class": re.compile(r"companyName|company-name", re.I)}]:
            el = soup.find(attrs=attr) if isinstance(attr, dict) and "data-company-name" not in attr else soup.find("div", attr)
            if el:
                company = el.get_text(strip=True)
                break

        # JD div
        for div_id in ["jobDescriptionText", "job-description"]:
            div = soup.find("div", id=div_id)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        for cls in [re.compile(r"jobsearch-jobDescriptionText", re.I), re.compile(r"job-description", re.I)]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Indeed failed: {e}")
        return None


async def _scrape_naukri(url: str) -> dict[str, str] | None:
    """Naukri: try internal API first, then HTML scrape."""
    try:
        # Try Naukri job API
        jid_match = re.search(r'-(\d{10,})', url)
        if jid_match:
            jid = jid_match.group(1)
            api_url = f"https://www.naukri.com/jobapi/v3/job/{jid}"
            try:
                async with httpx.AsyncClient(timeout=10.0, headers={
                    **_HEADERS, "appid": "109", "systemid": "Naukri", "Referer": url,
                }) as client:
                    resp = await client.get(api_url)
                    if resp.status_code == 200:
                        data = resp.json()
                        desc = (data.get("jobDetails", {}).get("description", "")
                                or data.get("jobDesc", ""))
                        company = data.get("companyDetail", {}).get("name", "")
                        if desc:
                            clean = BeautifulSoup(desc, "html.parser").get_text(separator="\n", strip=True)
                            if len(clean) >= 100:
                                return {"text": clean, "company": company}
            except Exception:
                pass

        # HTML fallback
        status, html = await _fetch_html(url, extra_headers={"Referer": "https://www.naukri.com/"})
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        # Script tag extraction
        for script in soup.find_all("script"):
            text = script.string or ""
            if "jobDescription" in text or '"description"' in text:
                for pattern in [
                    r'"jobDescription"\s*:\s*"((?:[^"\\]|\\.){100,})"',
                    r'"description"\s*:\s*"((?:[^"\\]|\\.){100,})"',
                ]:
                    m = re.search(pattern, text)
                    if m:
                        raw = m.group(1).encode().decode("unicode_escape", errors="ignore")
                        clean = BeautifulSoup(raw, "html.parser").get_text(separator="\n", strip=True)
                        if len(clean) >= 100:
                            return {"text": clean, "company": ""}

        for cls in [re.compile(r"job-desc|jd-desc|jobDescriptionContainer", re.I)]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": ""}

        text = _extract_full_text(soup)
        return {"text": text, "company": ""} if text else None
    except Exception as e:
        print(f"[SCRAPE] Naukri failed: {e}")
        return None


async def _scrape_glassdoor(url: str) -> dict[str, str] | None:
    """Glassdoor heavily blocks bots — try JSON-LD and full text."""
    try:
        status, html = await _fetch_html(url, extra_headers={"Referer": "https://www.glassdoor.com/"})
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find("div", class_=re.compile(r"employer-name|EmployerProfile", re.I))
        if el:
            company = el.get_text(strip=True)

        for cls in [re.compile(r"jobDescriptionContent|desc", re.I)]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Glassdoor failed: {e}")
        return None


async def _scrape_internshala(url: str) -> dict[str, str] | None:
    """Internshala is more scraper-friendly."""
    try:
        status, html = await _fetch_html(url, extra_headers={"Referer": "https://internshala.com/"})
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        company = ""
        el = soup.find("a", class_=re.compile(r"company-name|link_display_like_text", re.I))
        if el:
            company = el.get_text(strip=True)

        for cls in [
            re.compile(r"internship_details|job_description|about_company", re.I),
            re.compile(r"detail-container", re.I),
        ]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            if not jld.get("company"):
                jld["company"] = company
            return jld

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Internshala failed: {e}")
        return None


async def _scrape_wellfound(url: str) -> dict[str, str] | None:
    """Wellfound (AngelList) — JSON-LD usually present."""
    try:
        status, html = await _fetch_html(url)
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find("a", class_=re.compile(r"company|startup", re.I))
        if el:
            company = el.get_text(strip=True)

        for cls in [re.compile(r"job-description|description", re.I)]:
            div = soup.find("div", class_=cls)
            if div:
                return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Wellfound failed: {e}")
        return None


async def _scrape_greenhouse(url: str) -> dict[str, str] | None:
    """Greenhouse ATS — clean HTML, usually works well."""
    try:
        status, html = await _fetch_html(url)
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find("span", class_=re.compile(r"company-name", re.I))
        if el:
            company = el.get_text(strip=True)

        div = soup.find("div", id="content") or soup.find("div", class_=re.compile(r"job-post", re.I))
        if div:
            return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Greenhouse failed: {e}")
        return None


async def _scrape_lever(url: str) -> dict[str, str] | None:
    """Lever ATS — clean HTML."""
    try:
        status, html = await _fetch_html(url)
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find("a", class_=re.compile(r"main-header-logo", re.I))
        if el:
            company = el.get("title", "") or el.get_text(strip=True)

        div = soup.find("div", class_=re.compile(r"section-wrapper|posting-description", re.I))
        if div:
            return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Lever failed: {e}")
        return None


async def _scrape_workday(url: str) -> dict[str, str] | None:
    """Workday — JS-heavy but JSON-LD sometimes present."""
    try:
        status, html = await _fetch_html(url)
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        text = _extract_full_text(soup)
        return {"text": text, "company": ""} if text else None
    except Exception as e:
        print(f"[SCRAPE] Workday failed: {e}")
        return None


async def _scrape_monster(url: str) -> dict[str, str] | None:
    try:
        status, html = await _fetch_html(url, extra_headers={"Referer": "https://www.monster.com/"})
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find(class_=re.compile(r"company-name|companyName", re.I))
        if el:
            company = el.get_text(strip=True)

        div = soup.find("div", class_=re.compile(r"job-description|jobDescription", re.I))
        if div:
            return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] Monster failed: {e}")
        return None


async def _scrape_ziprecruiter(url: str) -> dict[str, str] | None:
    try:
        status, html = await _fetch_html(url, extra_headers={"Referer": "https://www.ziprecruiter.com/"})
        if status != 200:
            return None
        soup = BeautifulSoup(html, "html.parser")

        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            return jld

        company = ""
        el = soup.find(class_=re.compile(r"hiring_company_text|company", re.I))
        if el:
            company = el.get_text(strip=True)

        div = soup.find("div", class_=re.compile(r"jobDescriptionSection|job_description", re.I))
        if div:
            return {"text": div.get_text(separator="\n", strip=True), "company": company}

        text = _extract_full_text(soup)
        return {"text": text, "company": company} if text else None
    except Exception as e:
        print(f"[SCRAPE] ZipRecruiter failed: {e}")
        return None


# ── Generic fetch fallback ────────────────────────────────────────────────────

async def _generic_fetch(url: str, domain: str, portal_company: str) -> dict[str, str] | None:
    """Generic HTML fetch with JSON-LD and full-text fallback."""
    try:
        status, html = await _fetch_html(url)
        if status == 403:
            raise ValueError(
                f"The site ({domain}) blocked automated access (HTTP 403).\n"
                "Please open the job link in your browser, copy the description, "
                "and use 'Paste Text' instead."
            )
        if status == 404:
            raise ValueError("Job posting not found (HTTP 404). The link may have expired.")
        if status != 200:
            raise ValueError(
                f"Could not access the job URL (HTTP {status}). "
                "Please copy the job description text and use 'Paste Text'."
            )

        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD
        jld = _extract_jsonld(soup)
        if jld and len(jld.get("text", "")) >= 100:
            if not jld.get("company"):
                jld["company"] = portal_company
            return jld

        # Meta description
        meta_text = _extract_meta(soup)
        if meta_text and len(meta_text) >= 100:
            return {"text": meta_text, "company": portal_company}

        # Full page text
        text = _extract_full_text(soup)
        if text and len(text) >= 100:
            return {"text": text, "company": portal_company}

        return None
    except ValueError:
        raise
    except httpx.TimeoutException:
        raise ValueError(
            "The job page took too long to respond (timeout). "
            "It may be using bot protection (Cloudflare). "
            "Please copy the job description text and use 'Paste Text'."
        )
    except Exception as e:
        print(f"[SCRAPE] Generic fetch failed: {e}")
        return None


# ── Extraction helpers ────────────────────────────────────────────────────────

def _extract_jsonld(soup: BeautifulSoup) -> dict[str, str] | None:
    """Extract job description from JSON-LD schema.org/JobPosting."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "JobPosting":
                    desc = item.get("description", "")
                    org = item.get("hiringOrganization", {})
                    company = org.get("name", "") if isinstance(org, dict) else ""
                    if desc:
                        clean = BeautifulSoup(desc, "html.parser").get_text(separator="\n", strip=True)
                        return {"text": clean, "company": company}
                if "@graph" in item:
                    for node in item["@graph"]:
                        if isinstance(node, dict) and node.get("@type") == "JobPosting":
                            desc = node.get("description", "")
                            org = node.get("hiringOrganization", {})
                            company = org.get("name", "") if isinstance(org, dict) else ""
                            if desc:
                                clean = BeautifulSoup(desc, "html.parser").get_text(separator="\n", strip=True)
                                return {"text": clean, "company": company}
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def _extract_meta(soup: BeautifulSoup) -> str | None:
    og = soup.find("meta", property="og:description")
    if og and og.get("content") and len(og["content"]) >= 100:
        return og["content"]
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content") and len(meta["content"]) >= 100:
        return meta["content"]
    return None


def _extract_full_text(soup: BeautifulSoup) -> str | None:
    for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                     "noscript", "iframe", "svg", "form", "button"]):
        tag.extract()
    main = soup.find("main") or soup.find("article") or soup.find("div", role="main")
    target = main if main else (soup.body if soup.body else soup)
    text = target.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 3]
    text = "\n".join(lines)
    return text if len(text) >= 100 else None
