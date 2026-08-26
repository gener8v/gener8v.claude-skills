#!/usr/bin/env python3
"""gener8v pipeline state — deterministic scan of .gener8v/ (schema_version 3).

Regex first, model second. Everything Orchestrate can decide by looking at which files exist and
what their status lines say is decided here, so the model's attention is spent on recommendations.

Layout (see CONVENTIONS.md §2): living artifacts at the top level, change artifacts under
changes/<change-slug>/{change.md,tickets,delivery,reviews}. A legacy project with top-level
tickets/, delivery/ and reviews/*-review.md is read as the pseudo-change "initial".

Usage:
  gener8v-state.py state   [--root DIR] [--stdout [--json]]   # write .gener8v/pipeline-state.yaml (or print it; --json for CI)
  gener8v-state.py summary [--root DIR]              # short summary (what the SessionStart hook injects)
  gener8v-state.py lint    [--root DIR] [--src DIR]  # ID and coverage lints; exit 1 on ERROR
  gener8v-state.py metrics [--root DIR]              # derived metrics (YAML on stdout)

No third-party dependencies. Python 3.8+.
"""
import argparse
import datetime as _dt
import glob
import json
import os
import re
import statistics
import subprocess
import sys

# --------------------------------------------------------------------------- constants

ID_RE = re.compile(r"\b([A-Z]{2,4})-(REQ|NFR)-(\d{3,})\b")
TICKET_HEAD_RE = re.compile(r"^###\s+(TICKET-\d{3,})\s*:", re.M)
TICKET_ID_RE = re.compile(r"\bTICKET-\d{3,}\b")
FINDING_HEAD_RE = re.compile(r"^###\s+(CR|QR|SEC|DS|FIND)-\d{3,}\b", re.M)
SEVERITY_RE = re.compile(r"^\*\*Severity:\*\*\s*([A-Za-z ]+)", re.M)
VERDICT_BLOCKING = {"changes required", "improvements required", "remediation required"}
VERDICT_OK = {"approved", "approved with notes", "approved with observations", "approved with suggestions", "approved with accepted risk"}
PRIORITY_ORDER = {"must": 0, "should": 1, "could": 2}
SOURCE_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".swift", ".c", ".cc", ".cpp", ".h", ".scala", ".ex", ".exs", ".sql", ".sh")
SKIP_DIRS = {".git", "node_modules", ".gener8v", "dist", "build", "vendor", ".venv", "venv", "__pycache__", ".claude", "target", ".next"}
REVIEW_KINDS = ("code", "quality", "security")

# --------------------------------------------------------------------------- helpers


def slugify(name: str) -> str:
    """'Search & Retrieval' -> 'search-and-retrieval'. The one slug rule, in one place."""
    s = name.strip().lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def exists(path):
    return bool(path) and os.path.isfile(path)


def rel(base, path):
    return os.path.relpath(path, base) if exists(path) else None


def field(text, name):
    m = re.search(r"^\*\*" + re.escape(name) + r":\*\*\s*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or re.search(r"[:#\[\]{}&*!|>'\"%@`,?]|^\s|\s$", s) or s.lower() in ("null", "true", "false", "yes", "no", "~"):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def yaml_dump(obj, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                out.append(f"{pad}{k}:" + (" {}" if not v else ""))
                out.extend(yaml_dump(v, indent + 1))
            elif isinstance(v, list):
                if v and all(not isinstance(i, (dict, list)) for i in v):
                    out.append(f"{pad}{k}: [" + ", ".join(yaml_scalar(i) for i in v) + "]")
                else:
                    out.append(f"{pad}{k}:" + (" []" if not v else ""))
                    out.extend(yaml_dump(v, indent + 1))
            else:
                out.append(f"{pad}{k}: {yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                lines = yaml_dump(item, indent + 1)
                if lines:
                    out.append(f"{pad}- {lines[0].lstrip()}")
                    out.extend(lines[1:])
            else:
                out.append(f"{pad}- {yaml_scalar(item)}")
    return out


# --------------------------------------------------------------------------- parsing


def has_source_tree(root):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        n += sum(1 for f in filenames if f.endswith(SOURCE_EXT))
        if n >= 3:
            return True
    return False


def find_gener8v(root):
    d = os.path.join(root, ".gener8v")
    return d if os.path.isdir(d) else None


def prd_areas(prd_text):
    areas, in_section = [], False
    for line in prd_text.splitlines():
        if line.startswith("## "):
            in_section = line.strip().lower().startswith("## functional capabilities")
            continue
        if in_section and line.startswith("### "):
            name = line[4:].strip()
            name = re.sub(r"\s*\*\(withdrawn[^)]*\)\*\s*$", "", name, flags=re.I)
            areas.append(name)
    return areas


def first_h1(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def approved(text):
    st = (field(text, "Status") or "").strip().lower()
    return st.startswith("approved")


def parse_tickets(text):
    tickets = {}
    heads = list(TICKET_HEAD_RE.finditer(text))
    for i, m in enumerate(heads):
        tid = m.group(1)
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        title = body[: body.find("\n")].strip() if "\n" in body else body.strip()
        deps = TICKET_ID_RE.findall(field(body, "Depends On") or "")
        prio = (field(body, "Priority") or "").strip().split(" ")[0].strip("*") if field(body, "Priority") else None
        reqs = sorted({f"{p}-{k}-{n}" for p, k, n in ID_RE.findall(field(body, "Requirements Covered") or body)})
        tickets[tid] = {"title": title, "depends_on": deps, "priority": prio, "requirements": reqs, "body": body}
    return tickets


def parse_brief(text):
    """Affected Capability Areas table -> [(area name, kind, requirements cell)]."""
    rows = []
    in_tbl = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_tbl = line.strip().lower().startswith("## affected capability areas")
            continue
        if in_tbl and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0].lower() not in ("area", "---") and not set(cells[0]) <= set("-: "):
                rows.append((cells[0], cells[1], cells[2]))
    return rows


def deferred_kinds(dtext):
    raw = field(dtext, "Reviews Deferred") or ""
    kinds_part = re.split(r"\s+[—–-]\s+|:", raw, maxsplit=1)[0].lower() if raw else ""
    if not kinds_part or kinds_part.strip().startswith("none"):
        return []
    return [k for k in REVIEW_KINDS if re.search(r"\b" + k + r"\b", kinds_part)]


# --------------------------------------------------------------------------- scan


def scan_change(g, slug, cdir, legacy, delivered_areas_index):
    """Scan one change directory (or the legacy top level) -> change entry + flat ticket list."""
    brief_path = None if legacy else os.path.join(cdir, "change.md")
    brief = read(brief_path) if brief_path else ""
    entry = {
        "brief": rel(g, brief_path) if brief_path else None,
        "legacy": legacy,
        "title": first_h1(brief) if brief else ("Initial (legacy layout)" if legacy else slug),
        "declared_status": field(brief, "Status") if brief else None,
        "approved": approved(brief) or (field(brief, "Status") or "").lower().startswith(("in delivery", "complete")) if brief else None,
        "areas": [],
        "areas_detail": {},
        "pending_specification": [],
        "pending_breakdown": [],
        "deliveries": {},
        "progress": {"total": 0, "delivered": 0, "reviewed": 0, "done": 0, "changes_required": 0},
    }
    flat = []
    tdir, ddir, rdir = (os.path.join(cdir, "tickets"), os.path.join(cdir, "delivery"), os.path.join(cdir, "reviews"))
    ticket_files = sorted(glob.glob(os.path.join(tdir, "*.md")))
    brief_rows = parse_brief(brief) if brief else []
    for area_name, kind, reqs_cell in brief_rows:
        aslug = slugify(area_name)
        entry["areas"].append(aslug)
        if "pending" in reqs_cell.lower() or not ID_RE.search(reqs_cell):
            entry["pending_specification"].append(aslug)
        if not exists(os.path.join(tdir, f"{aslug}.md")):
            entry["pending_breakdown"].append(aslug)
    for tf in ticket_files:
        aslug = os.path.splitext(os.path.basename(tf))[0]
        if aslug not in entry["areas"]:
            entry["areas"].append(aslug)
        tickets = parse_tickets(read(tf))
        entry["areas_detail"][aslug] = {"tickets": rel(g, tf), "ticket_count": len(tickets)}
        delivered_ids = set()
        for tid in tickets:
            dp = os.path.join(ddir, f"{aslug}-{tid.lower()}-delivery.md")
            if exists(dp) and (field(read(dp), "Status") or "").lower().startswith("delivered"):
                delivered_ids.add(tid)
        for tid, t in tickets.items():
            dp = os.path.join(ddir, f"{aslug}-{tid.lower()}-delivery.md")
            dtext = read(dp) if exists(dp) else ""
            dstatus = (field(dtext, "Status") or "").strip() if dtext else None
            reviews, verdicts = {}, {}
            for kind in REVIEW_KINDS:
                rp = os.path.join(rdir, f"{aslug}-{tid.lower()}-{kind}-review.md")
                reviews[kind] = rel(g, rp)
                verdicts[kind] = field(read(rp), "Result") if exists(rp) else None
            unmet = [d for d in t["depends_on"] if d not in delivered_ids]
            verification = ((field(dtext, "Verification") or "not run").strip().lower() if dtext else None)
            deferred = deferred_kinds(dtext) if dtext else []
            ok = lambda k: (reviews[k] and (verdicts[k] or "").strip().lower() in VERDICT_OK) or k in deferred
            if not dtext:
                status = "blocked" if unmet else "ready"
            elif not dstatus.lower().startswith("delivered"):
                s = dstatus.lower()
                status = ("in_progress" if s.startswith("in progress") else "reconciled" if s.startswith("reconciled")
                          else "blocked_delivery" if s.startswith("blocked") else "partial" if s.startswith("partial") else s.split()[0])
            elif any((v or "").strip().lower() in VERDICT_BLOCKING for v in verdicts.values()):
                status = "changes_required"
            elif all(ok(k) for k in REVIEW_KINDS):
                status = "reviewed"
            else:
                status = "delivered"
            done = status == "reviewed" and (verification or "").startswith("passed")
            amend = bool(dtext) and bool(re.search(r"^## Post-Review Amendments\s*\n+(?!\s*None\b)\S", dtext, re.M))
            e = {
                "title": t["title"], "priority": t["priority"], "status": status, "done": done,
                "depends_on": t["depends_on"], "requirements": t["requirements"],
                "delivery": rel(g, dp), "delivery_status": dstatus, "verification": verification,
                "code_review": reviews["code"], "quality_review": reviews["quality"], "security_review": reviews["security"],
                "reviews_deferred": deferred, "verdicts": {k: v for k, v in verdicts.items() if v},
                "amended_after_review": amend,
            }
            key = f"{aslug}/{tid}"
            entry["deliveries"][key] = e
            flat.append((slug, aslug, tid, e, unmet))
            if status in ("delivered", "reviewed", "changes_required"):
                delivered_areas_index.setdefault(aslug, set()).add(slug)
    p = entry["progress"]
    p["total"] = len(entry["deliveries"])
    p["delivered"] = sum(1 for e in entry["deliveries"].values() if e["status"] in ("delivered", "reviewed", "changes_required"))
    p["reviewed"] = sum(1 for e in entry["deliveries"].values() if e["status"] == "reviewed")
    p["done"] = sum(1 for e in entry["deliveries"].values() if e["done"])
    p["changes_required"] = sum(1 for e in entry["deliveries"].values() if e["status"] == "changes_required")
    # working status + stage
    decl = (entry["declared_status"] or "").lower()
    if decl.startswith("abandoned"):
        status, stage = "abandoned", "abandoned"
    elif p["total"] == 0:
        status = "planned"
        stage = "breaking_down" if entry["areas"] else "planned"
    elif p["done"] == p["total"]:
        status, stage = "complete", "reviewed"
    elif p["delivered"] == 0 and not any(e["status"] in ("in_progress", "reconciled", "partial", "blocked_delivery") for e in entry["deliveries"].values()):
        status, stage = "ready", "ready_for_delivery"
    elif p["delivered"] < p["total"]:
        status, stage = "in_delivery", "delivering"
    elif p["reviewed"] + p["changes_required"] == 0:
        status, stage = "in_delivery", "delivered"
    else:
        status, stage = "in_delivery", "reviewing"
    entry["status"], entry["stage"] = status, stage
    if decl.startswith("complete") and status != "complete":
        entry["warning"] = f"change '{slug}' is declared Complete but {p['total'] - p['done']} ticket(s) are not done"
    if decl.startswith("draft") and p["total"] > 0:
        entry["warning"] = f"change '{slug}' is still Draft but has tickets — approve the brief (Product Owner)"
    return entry, flat


def scan(root):
    g = find_gener8v(root)
    state = {
        "generated": now_iso(), "schema_version": 3, "stage": "not_started", "prd_title": None,
        "system_context": False, "has_source": has_source_tree(root), "active_changes": [], "approvals_pending": 0,
        "capability_areas": {}, "changes": {}, "cross_cutting": {}, "next_steps": [], "warnings": [], "totals": {},
    }
    if not g:
        entry = "brownfield" if state["has_source"] else "planning"
        state["next_steps"] = [
            {"skill": "setup", "target": "project root", "reason": "No .gener8v/ directory — bootstrap the pipeline"},
            {"skill": entry, "target": "project", "reason": "Existing source code — map it before planning new work" if state["has_source"] else "No source yet — start from intent"},
        ]
        return state, g

    prd_text = read(os.path.join(g, "prd.md"))
    state["system_context"] = exists(os.path.join(g, "context.md"))
    cc = {
        "dependency_map": rel(g, os.path.join(g, "dependencies", "dependency-map.md")),
        "system_design": rel(g, os.path.join(g, "technical-design", "system-design.md")),
        "prd_constraints": rel(g, os.path.join(g, "constraints", "prd.md")),
        "brownfield_checkpoints": sorted(rel(g, p) for p in glob.glob(os.path.join(g, "brownfield", "*.md"))),
        "audits": sorted(rel(g, p) for p in glob.glob(os.path.join(g, "audits", "*.md"))),
        "flows": sorted(rel(g, p) for p in glob.glob(os.path.join(g, "flows", "*.md"))),
        "sweeps": sorted(rel(g, p) for p in glob.glob(os.path.join(g, "sweeps", "*.md"))),
        "assessments": sorted(rel(g, p) for p in glob.glob(os.path.join(g, "reviews", "*-assessment.md"))),
        "legacy_layout": bool(glob.glob(os.path.join(g, "tickets", "*.md")) or glob.glob(os.path.join(g, "delivery", "*.md"))),
    }
    state["cross_cutting"] = cc

    if not prd_text:
        state["stage"] = "not_started"
        has_specs = bool(glob.glob(os.path.join(g, "specifications", "*.md")))
        standalone = [k for k in ("flows", "sweeps", "assessments") if cc.get(k)]
        if has_specs or cc["brownfield_checkpoints"]:
            state["warnings"].append("Brownfield is mid-run: checkpoints/specifications exist but .gener8v/prd.md is missing (Phase 5 writes the PRD)")
            state["next_steps"].append({"skill": "brownfield", "target": "resume", "reason": "Resume at the first phase whose output is missing"})
        else:
            if standalone:
                state["warnings"].append("Standalone artifacts present without a PRD: " + ", ".join(standalone) + " — the project is not on the pipeline yet; Setup keeps them")
            if not exists(os.path.join(g, "CONVENTIONS.md")):
                state["next_steps"].append({"skill": "setup", "target": "project root", "reason": "No PRD and no CONVENTIONS.md — bootstrap the pipeline"})
            if state["has_source"]:
                state["next_steps"].append({"skill": "brownfield", "target": "project", "reason": "Existing source code and no PRD — map it into the pipeline"})
            else:
                state["next_steps"].append({"skill": "planning", "target": "user prompt", "reason": "No PRD and no source yet — start from intent"})
        return state, g

    state["prd_title"] = first_h1(prd_text)
    state["prd_approved"] = approved(prd_text)
    areas = prd_areas(prd_text)
    if not areas:
        state["warnings"].append("PRD has no '### ' capability areas under '## Functional Capabilities'")
    known_slugs = {slugify(a) for a in areas}
    for p in glob.glob(os.path.join(g, "specifications", "*.md")):
        s = os.path.splitext(os.path.basename(p))[0]
        if s not in known_slugs:
            state["warnings"].append(f"specifications/{s}.md has no matching capability area in the PRD (orphaned or renamed area)")

    approvals_pending = 0 if state["prd_approved"] else 1
    totals = {"areas": len(areas), "specs": 0, "changes": 0, "tickets_total": 0, "delivered": 0, "reviewed": 0, "done": 0, "changes_required": 0}
    # living coverage
    for area in areas:
        slug = slugify(area)
        sp = os.path.join(g, "specifications", f"{slug}.md")
        stext = read(sp) if exists(sp) else ""
        ids = ID_RE.findall(stext)
        a = {
            "name": area,
            "specification": rel(g, sp),
            "approved": approved(stext) if stext else None,
            "requirements": sum(1 for _, k, _ in ids if k == "REQ"),
            "nfrs": sum(1 for _, k, _ in ids if k == "NFR"),
            "constraints": rel(g, os.path.join(g, "constraints", f"{slug}.md")),
            "technical_design": rel(g, os.path.join(g, "technical-design", f"{slug}.md")),
            "changes": [],
        }
        if stext:
            totals["specs"] += 1
            if not a["approved"]:
                approvals_pending += 1
        for kp in (a["constraints"], a["technical_design"]):
            if kp and not approved(read(os.path.join(g, kp))):
                approvals_pending += 1
        state["capability_areas"][slug] = a

    for kp in (cc["prd_constraints"], cc["dependency_map"], cc["system_design"]):
        if kp and not approved(read(os.path.join(g, kp))):
            approvals_pending += 1

    # changes (+ legacy)
    delivered_index = {}
    all_tickets = []
    change_dirs = sorted(d for d in glob.glob(os.path.join(g, "changes", "*")) if os.path.isdir(d))
    for cdir in change_dirs:
        slug = os.path.basename(cdir)
        entry, flat = scan_change(g, slug, cdir, False, delivered_index)
        state["changes"][slug] = entry
        all_tickets.extend(flat)
    if cc["legacy_layout"]:
        entry, flat = scan_change(g, "initial", g, True, delivered_index)
        state["changes"]["initial"] = entry
        all_tickets.extend(flat)
        state["warnings"].append("Legacy layout: tickets/, delivery/ and reviews/*-review.md at the top level are read as change 'initial' — migrate with `git mv tickets delivery changes/initial/` (and reviews/*-review.md into changes/initial/reviews/)")
    for slug, ch in state["changes"].items():
        totals["changes"] += 1
        for aslug in ch["areas"]:
            if aslug in state["capability_areas"] and slug not in state["capability_areas"][aslug]["changes"]:
                state["capability_areas"][aslug]["changes"].append(slug)
            elif aslug not in state["capability_areas"]:
                state["warnings"].append(f"change '{slug}' names area '{aslug}' which is not in the PRD")
        if ch.get("warning"):
            state["warnings"].append(ch.pop("warning"))
        if ch["brief"] and ch["approved"] is False:
            approvals_pending += 1
        p = ch["progress"]
        for k in ("delivered", "reviewed", "done", "changes_required"):
            totals[k] += p[k]
        totals["tickets_total"] += p["total"]
    state["active_changes"] = [s for s, ch in state["changes"].items() if ch["status"] in ("ready", "in_delivery")]
    if len(state["active_changes"]) > 1:
        state["warnings"].append("Several changes are active (" + ", ".join(state["active_changes"]) + ") — name the change when invoking per-ticket skills")
    state["approvals_pending"] = approvals_pending

    # brownfield-onboarded: every spec carries a populated @spec Coverage table and no change has tickets
    spec_paths = [os.path.join(g, a["specification"]) for a in state["capability_areas"].values() if a["specification"]]
    if spec_paths and totals["tickets_total"] == 0 and all(re.search(r"^## @spec Coverage\s*$.*?\|\s*[A-Z]{2,4}-(REQ|NFR)-\d+", read(p), re.S | re.M) for p in spec_paths):
        state["brownfield_onboarded"] = True
        state["warnings"].append("Brownfield-onboarded: the code these specifications describe already exists — the next step is a change (/planning), not re-delivery")

    # ---- overall stage
    n = len(areas)
    active = [state["changes"][s] for s in state["active_changes"]]
    if n == 0 or totals["specs"] == 0:
        stage = "planning_complete"
    elif active:
        stage = active[0]["stage"]
    elif totals["specs"] < n:
        stage = "specifying"
    elif state["changes"] and all(ch["status"] in ("complete", "abandoned") for ch in state["changes"].values()):
        stage = "audited" if cc["audits"] else "reviewed"
    elif any(ch["status"] == "planned" for ch in state["changes"].values()):
        stage = "breaking_down"
    else:
        any_design = any(a["technical_design"] for a in state["capability_areas"].values()) or cc["system_design"]
        any_constraints = any(a["constraints"] for a in state["capability_areas"].values()) or cc["prd_constraints"] or cc["dependency_map"]
        stage = "designing" if any_design else "analyzing" if any_constraints else "analyzing"
    state["stage"] = stage

    # ---- next steps
    steps = []
    add = lambda skill, target, reason: steps.append({"skill": skill, "target": target, "reason": reason})
    prio = lambda e: PRIORITY_ORDER.get((e["priority"] or "").lower(), 3)
    for cslug, aslug, tid, e, unmet in all_tickets:
        if e["status"] == "in_progress":
            add("delivery", f"{aslug} {tid} in {cslug}", "Delivery record is In Progress — resume from its Implementation Plan and Progress checklist")
        elif e["status"] == "reconciled":
            add("delivery", f"{aslug} {tid} in {cslug}", "Reconciled (Go) but the plan is not yet approved — present the plan")
        elif e["status"] == "blocked_delivery":
            add("delivery", f"{aslug} {tid} in {cslug}", "Pre-flight reconciliation found blocking assumptions — see the record's Blocking findings")
    for cslug, aslug, tid, e, unmet in all_tickets:
        if e["status"] == "changes_required":
            bad = ", ".join(f"{k}: {v}" for k, v in e["verdicts"].items() if v.strip().lower() in VERDICT_BLOCKING)
            add("delivery", f"{aslug} {tid} in {cslug}", f"Review verdict blocks completion ({bad}) — resolve the findings, then re-review")
    for cslug, aslug, tid, e, unmet in all_tickets:
        if e["status"] == "delivered":
            missing = [k for k in ("code_review", "quality_review", "security_review") if not e[k] and k.split("_")[0] not in e["reviews_deferred"]]
            add("+".join(m.replace("_", "-") for m in missing), f"{aslug} {tid} in {cslug}", "Delivered; run the missing reviews' findings phases in parallel")
        elif e["status"] == "reviewed" and not e["done"]:
            add("delivery", f"{aslug} {tid} in {cslug}", f"Reviews approved but Verification is '{e['verification']}' — run the checks and record them")
    ready = sorted([x for x in all_tickets if x[3]["status"] == "ready"], key=lambda x: (prio(x[3]), x[0], x[2]))
    for cslug, aslug, tid, e, unmet in ready:
        add("delivery", f"{aslug} {tid} in {cslug}", f"Ready ({e['priority'] or 'no priority set'}); all dependencies delivered")
    for area in areas:
        slug = slugify(area)
        if not state["capability_areas"][slug]["specification"]:
            add("specification", area, "No specification for this capability area")
    for cslug, ch in state["changes"].items():
        if ch["status"] in ("complete", "abandoned"):
            continue
        for aslug in ch["pending_specification"]:
            add("specification", f"{aslug} for {cslug}", "The change brief lists this area with requirements pending specification")
        for aslug in ch["pending_breakdown"]:
            if aslug not in ch["pending_specification"]:
                add("ticket-breakdown", f"{aslug} for {cslug}", "Specified for this change, no ticket breakdown yet")
    if state["changes"] == {} and totals["specs"] > 0 and not state.get("brownfield_onboarded"):
        add("planning", "first change", "Specifications exist but no change has been opened — open one to start ticket breakdown")
    if state.get("brownfield_onboarded"):
        add("planning", "first change", "Brownfield baseline complete — open a change for the first piece of new work")
    if n > 1 and not cc["dependency_map"] and totals["specs"] > 0:
        add("dependencies", "PRD", "Multiple capability areas and no dependency map (optional for light scope)")
    if stage in ("reviewed",) and not cc["audits"]:
        add("audit", "pipeline", "Every change is complete; run a cross-stage audit")
    state["next_steps"] = steps
    state["totals"] = totals
    return state, g


# --------------------------------------------------------------------------- metrics


def git_first_date(root, path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%aI", "--", path], cwd=root, capture_output=True, text=True, timeout=10)
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        return _dt.datetime.fromisoformat(lines[-1]) if lines else None
    except Exception:
        return None


def git_last_date(root, path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%aI", "--", path], cwd=root, capture_output=True, text=True, timeout=10)
        s = out.stdout.strip()
        return _dt.datetime.fromisoformat(s) if s else None
    except Exception:
        return None


def compute_metrics(root):
    state, g = scan(root)
    m = {"generated": now_iso(), "tickets": {}, "reviews": {}, "findings": {}, "rework": {}, "verification": {}, "sweeps": {}, "approvals_pending": state.get("approvals_pending", 0), "sessions": 0, "lead_time_days": {}}
    if not g:
        return m
    entries = [(cs, key, e) for cs, ch in state["changes"].items() for key, e in ch["deliveries"].items()]
    m["tickets"] = {
        "total": len(entries),
        "done": sum(1 for _, _, e in entries if e["done"]),
        "changes_required_now": sum(1 for _, _, e in entries if e["status"] == "changes_required"),
        "by_priority": {p: sum(1 for _, _, e in entries if (e["priority"] or "").lower() == p) for p in ("must", "should", "could")},
        "no_priority": sum(1 for _, _, e in entries if not e["priority"]),
    }
    for kind in REVIEW_KINDS:
        dist = {"approved": 0, "approved_with_notes": 0, "changes_required": 0, "other": 0}
        counts, sev = 0, {}
        for _, _, e in entries:
            v = (e["verdicts"].get(kind) or "").strip().lower()
            if v:
                dist["approved" if v == "approved" else "approved_with_notes" if v in VERDICT_OK else "changes_required" if v in VERDICT_BLOCKING else "other"] += 1
            rp = e.get(f"{kind}_review")
            if rp:
                text = read(os.path.join(g, rp))
                counts += len(FINDING_HEAD_RE.findall(text))
                for s in SEVERITY_RE.findall(text):
                    sev[s.strip().lower()] = sev.get(s.strip().lower(), 0) + 1
        m["reviews"][kind] = dist
        m["findings"][kind] = {"total": counts, "by_severity": dict(sorted(sev.items()))}
    reviewed = [e for _, _, e in entries if e["status"] in ("reviewed", "changes_required")]
    m["rework"] = {
        "tickets_reviewed": len(reviewed),
        "tickets_amended_after_review": sum(1 for e in reviewed if e["amended_after_review"]),
        "rate": round(sum(1 for e in reviewed if e["amended_after_review"]) / len(reviewed), 2) if reviewed else None,
    }
    ver = [e["verification"] for _, _, e in entries if e["delivery"]]
    m["verification"] = {k: sum(1 for v in ver if (v or "").startswith(k)) for k in ("passed", "failed", "not run")}
    m["reviews_deferred"] = sum(len(e["reviews_deferred"]) for _, _, e in entries)
    sweeps = state["cross_cutting"].get("sweeps") or []
    open_ds = 0
    for sp in sweeps:
        text = read(os.path.join(g, sp))
        open_ds += len(re.findall(r"^### DS-\d{3,}", text, re.M))
    m["sweeps"] = {"count": len(sweeps), "findings": open_ds}
    runs = os.path.join(g, "runs.jsonl")
    if exists(runs):
        m["sessions"] = sum(1 for line in read(runs).splitlines() if '"session_start"' in line)
    # lead time from git: ticket file first commit -> delivery record last commit (Delivered)
    days = []
    for cs, ch in state["changes"].items():
        for key, e in ch["deliveries"].items():
            if not (e["delivery"] and (e["delivery_status"] or "").lower().startswith("delivered")):
                continue
            aslug = key.split("/")[0]
            tf = ch["areas_detail"].get(aslug, {}).get("tickets")
            if not tf:
                continue
            t0 = git_first_date(root, os.path.join(".gener8v", tf))
            t1 = git_last_date(root, os.path.join(".gener8v", e["delivery"]))
            if t0 and t1 and t1 >= t0:
                days.append((t1 - t0).total_seconds() / 86400)
    if days:
        m["lead_time_days"] = {"median": round(statistics.median(days), 1), "max": round(max(days), 1), "samples": len(days)}
    else:
        m["lead_time_days"] = {"median": None, "samples": 0, "note": "needs git history for ticket files and delivery records"}
    return m


# --------------------------------------------------------------------------- commands

HEADER = "# gener8v pipeline state — GENERATED by gener8v-state.py; do not edit by hand.\n# Regenerate: python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py\" state  (or /orchestrate)\n"


def public_state(state):
    """Drop internal fields before writing."""
    out = json.loads(json.dumps(state))
    for ch in out.get("changes", {}).values():
        for e in ch.get("deliveries", {}).values():
            e.pop("amended_after_review", None)
    return out


def cmd_state(args):
    state, g = scan(args.root)
    if args.json:
        sys.stdout.write(json.dumps(public_state(state), indent=2) + "\n")
        return 0
    text = HEADER + "\n".join(yaml_dump(public_state(state))) + "\n"
    if args.stdout or not g:
        sys.stdout.write(text)
        return 0
    out = os.path.join(g, "pipeline-state.yaml")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    if not args.quiet:
        print(f"wrote {os.path.relpath(out, args.root)} (stage: {state['stage']})")
    return 0


def cmd_summary(args):
    state, g = scan(args.root)
    if not g:
        print("gener8v: no .gener8v/ directory in this project.")
        return 0
    t = state.get("totals", {})
    lines = [f"gener8v pipeline — {state.get('prd_title') or '(no PRD)'}"]
    lines.append(f"stage: {state['stage']} · areas: {t.get('areas', 0)} · specs: {t.get('specs', 0)}/{t.get('areas', 0)} · changes: {t.get('changes', 0)} · tickets: {t.get('tickets_total', 0)} · delivered: {t.get('delivered', 0)} · done: {t.get('done', 0)}"
                 + (f" · changes required: {t['changes_required']}" if t.get("changes_required") else "")
                 + (f" · approvals pending: {state['approvals_pending']}" if state.get("approvals_pending") else ""))
    if state["active_changes"]:
        lines.append("active change" + ("s" if len(state["active_changes"]) > 1 else "") + ": " + ", ".join(f"{s} ({state['changes'][s]['stage']})" for s in state["active_changes"]))
    cc = state["cross_cutting"]
    extras = [k for k in ("dependency_map", "system_design", "prd_constraints") if cc.get(k)]
    counts = {k: len(cc.get(k) or []) for k in ("audits", "flows", "sweeps", "assessments", "brownfield_checkpoints")}
    lines.append("cross-cutting: " + ", ".join(extras + [f"{k}: {v}" for k, v in counts.items() if v]) if (extras or any(counts.values())) else "cross-cutting: none yet")
    for w in state.get("warnings", []):
        lines.append(f"warning: {w}")
    if state["next_steps"]:
        lines.append("next:")
        for s in state["next_steps"][: args.limit]:
            lines.append(f"  - /{s['skill']} {s['target']} — {s['reason']}")
        if len(state["next_steps"]) > args.limit:
            lines.append(f"  … {len(state['next_steps']) - args.limit} more in .gener8v/pipeline-state.yaml")
    print("\n".join(lines))
    return 0


def cmd_metrics(args):
    m = compute_metrics(args.root)
    sys.stdout.write("\n".join(yaml_dump(m)) + "\n")
    return 0


def cmd_lint(args):
    g = find_gener8v(args.root)
    if not g:
        print("no .gener8v/ directory")
        return 0
    errors, warns = [], []
    # 1. prefixes unique across specs; one prefix per spec
    prefix_owner, spec_ids = {}, {}
    for p in sorted(glob.glob(os.path.join(g, "specifications", "*.md"))):
        slug = os.path.splitext(os.path.basename(p))[0]
        ids = ID_RE.findall(read(p))
        prefixes = {pre for pre, _, _ in ids}
        spec_ids[slug] = {f"{pre}-{k}-{num}": k for pre, k, num in ids}
        if len(prefixes) > 1:
            warns.append(f"specifications/{slug}.md uses several requirement prefixes: {', '.join(sorted(prefixes))}")
        for pre in prefixes:
            if pre in prefix_owner and prefix_owner[pre] != slug:
                errors.append(f"requirement prefix {pre}- is used by both specifications/{prefix_owner[pre]}.md and specifications/{slug}.md")
            prefix_owner.setdefault(pre, slug)
        if not ids:
            warns.append(f"specifications/{slug}.md has no [PREFIX]-REQ-XXX requirements")
    # 2. coverage: every REQ/NFR appears in some ticket file (any change, legacy included) or has an @spec Coverage row
    ticket_files = glob.glob(os.path.join(g, "changes", "*", "tickets", "*.md")) + glob.glob(os.path.join(g, "tickets", "*.md"))
    covered = set()
    for tf in ticket_files:
        covered |= {f"{p}-{k}-{n}" for p, k, n in ID_RE.findall(read(tf))}
        body = read(tf)
        cslug = os.path.basename(os.path.dirname(os.path.dirname(tf))) if "/changes/" in tf.replace(os.sep, "/") else "initial"
        for m in TICKET_HEAD_RE.finditer(body):
            seg_end = body.find("\n### ", m.end())
            seg = body[m.end(): seg_end if seg_end != -1 else len(body)]
            for sec in ("Prior Art", "Output", "Known Hazards", "Acceptance Criteria", "Priority", "Value"):
                if f"**{sec}:**" not in seg:
                    warns.append(f"{cslug}/{os.path.basename(tf)} {m.group(1)} lacks a **{sec}:** section")
    for slug, ids in spec_ids.items():
        stext = read(os.path.join(g, "specifications", f"{slug}.md"))
        cov_rows = {f"{p}-{k}-{n}" for p, k, n in ID_RE.findall(stext.split("## @spec Coverage")[-1])} if "## @spec Coverage" in stext else set()
        missing_req = sorted(i for i, k in ids.items() if k == "REQ" and i not in covered and i not in cov_rows)
        missing_nfr = sorted(i for i, k in ids.items() if k == "NFR" and i not in covered and i not in cov_rows)
        if missing_req and ticket_files:
            errors.append(f"specifications/{slug}.md requirements in no ticket and no @spec Coverage row: {', '.join(missing_req[:10])}" + (" …" if len(missing_req) > 10 else ""))
        if missing_nfr and ticket_files:
            warns.append(f"specifications/{slug}.md NFRs in no ticket: {', '.join(missing_nfr)}")
        for n in re.findall(r"^- \*\*[A-Z]{2,4}-NFR-\d+\*\*.*$", stext, re.M):
            if "verified by" not in n.lower():
                warns.append(f"specifications/{slug}.md: {n[:60]}… names no verification method")
    # 3. @spec annotation coverage for delivered requirements
    src = args.src or args.root
    annotated = set()
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith((".md", ".yaml", ".yml", ".json", ".lock", ".txt", ".svg", ".png", ".jpg")):
                continue
            text = read(os.path.join(dirpath, fn))
            if "@spec" in text:
                for line in text.splitlines():
                    if "@spec" in line:
                        annotated.update(f"{p}-{k}-{n}" for p, k, n in ID_RE.findall(line))
    for p in sorted(glob.glob(os.path.join(g, "changes", "*", "delivery", "*-delivery.md")) + glob.glob(os.path.join(g, "delivery", "*-delivery.md"))):
        dtext = read(p)
        if not (field(dtext, "Status") or "").lower().startswith("delivered"):
            continue
        reqs = {f"{pre}-{k}-{num}" for pre, k, num in ID_RE.findall(field(dtext, "Requirements Covered") or "") if k == "REQ"}
        if not reqs:
            reqs = {f"{pre}-{k}-{num}" for pre, k, num in ID_RE.findall(dtext) if k == "REQ"}
        missing = sorted(r for r in reqs if r not in annotated)
        if missing:
            warns.append(f"{os.path.relpath(p, g)}: no @spec annotation found in source for {', '.join(missing)}")
    # 4. dangling references
    known = set().union(*[set(d) for d in spec_ids.values()]) if spec_ids else set()
    if known:
        for p in sorted(ticket_files + glob.glob(os.path.join(g, "changes", "*", "*.md")) + glob.glob(os.path.join(g, "changes", "*", "*", "*.md")) + glob.glob(os.path.join(g, "delivery", "*.md")) + glob.glob(os.path.join(g, "reviews", "*.md")) + glob.glob(os.path.join(g, "technical-design", "*.md")) + glob.glob(os.path.join(g, "constraints", "*.md"))):
            refs = {f"{pre}-{k}-{num}" for pre, k, num in ID_RE.findall(read(p))}
            dangling = sorted(refs - known)
            if dangling:
                warns.append(f"{os.path.relpath(p, g)} references requirement IDs that exist in no specification: {', '.join(dangling[:8])}" + (" …" if len(dangling) > 8 else ""))
    # 5. change briefs: areas exist, requirements cells match spec tags
    for bp in sorted(glob.glob(os.path.join(g, "changes", "*", "change.md"))):
        cslug = os.path.basename(os.path.dirname(bp))
        for area_name, kind, cell in parse_brief(read(bp)):
            aslug = slugify(area_name)
            spec = read(os.path.join(g, "specifications", f"{aslug}.md"))
            ids = ID_RE.findall(cell)
            for pre, k, num in ids:
                if spec and f"{pre}-{k}-{num}" not in spec:
                    errors.append(f"changes/{cslug}/change.md lists {pre}-{k}-{num} for {area_name} but specifications/{aslug}.md does not contain it")
            if ids and spec and f"change: {cslug}" not in spec and f"by {cslug}" not in spec:
                warns.append(f"specifications/{aslug}.md has no requirement tagged with change '{cslug}' although the brief lists deltas for it")
    for e in errors:
        print(f"ERROR {e}")
    for w in warns:
        print(f"WARN  {w}")
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["state", "summary", "lint", "metrics"])
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ap.add_argument("--stdout", action="store_true", help="state: print instead of writing the file")
    ap.add_argument("--json", action="store_true", help="state: print JSON to stdout (implies --stdout; no dependencies for CI gates)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--limit", type=int, default=6, help="summary: max next steps to show")
    ap.add_argument("--src", default=None, help="lint: source root to grep for @spec (default: --root)")
    args = ap.parse_args(argv)
    return {"state": cmd_state, "summary": cmd_summary, "lint": cmd_lint, "metrics": cmd_metrics}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
