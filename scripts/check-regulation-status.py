#!/usr/bin/env python3
"""Validate and audit dated regulation status snapshots in registry/regulation/.

Why this exists (SecID#228):
  A regulation or bill's lifecycle status in `match_nodes[].data.notes` is a
  dated snapshot (`Status: <State> (...; verified as of YYYY-MM-DD)`), never a
  timeless truth. Bills advance through readings and committees, die on the
  order paper at prorogation/dissolution, get reintroduced under the same or a
  different number in a new session, or receive Royal Assent; enacted statutes
  commence in phases or get amended.

  Three rules govern regulation status snapshots:
    1. Every `Status:` note in `registry/regulation/` MUST carry an explicit
       ISO verification date (`verified as of YYYY-MM-DD`).
    2. The snapshot is for finding and sorting — never a substitute for
       checking the live primary source before stating a bill's or statute's
       current legal status.
    3. Terminal states (`Enacted`, `In force`, `Died on the Order Paper`) are
       NOT exempt from scheduled re-verification, though their re-check cadence
       is longer than active bills (`--max-age-days-terminal`, default 180 days,
       vs `--max-age-days-proposed`, default 90 days).

Usage:
  python3 scripts/check-regulation-status.py               # Offline format + age audit
  python3 scripts/check-regulation-status.py --self-test   # Unit tests for parser + live comparator
  python3 scripts/check-regulation-status.py --live        # Query machine-readable legislative APIs (e.g. LEGISinfo JSON)
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from _net_guard import effective_url_is_safe

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGULATION_GLOB = os.path.join(REPO_ROOT, "registry", "regulation", "**", "*.json")

STATUS_PREFIX_RE = re.compile(r"(?:^|\b)Status:\s*(?P<body>[^\n]+)")
STATUS_CLAUSE_RE = re.compile(
    r"(?:^|\b)Status:\s*(?P<clause>[^\n]*?\bverified as of (?P<date>\d{4}-\d{2}-\d{2})\)?\.?)"
)
VERIFIED_DATE_RE = re.compile(r"\bverified as of (\d{4}-\d{2}-\d{2})\b")
LEGISINFO_JSON_RE = re.compile(
    r"^https://www\.parl\.ca/legisinfo/en/bill/\d+-\d+/[a-z]-\d+/json$",
    re.IGNORECASE,
)


def classify_status_state(status_body: str) -> str:
    """Classify a Status: clause into 'proposed' or 'terminal' (`enacted`/`in_force`/`died`)."""
    lowered = status_body.strip().lower()
    if lowered.startswith("proposed") or lowered.startswith("pending") or lowered.startswith("draft"):
        return "proposed"
    if lowered.startswith("enacted"):
        return "enacted"
    if lowered.startswith("in force"):
        return "in_force"
    if lowered.startswith("died on the order paper") or lowered.startswith("withdrawn"):
        return "died"
    return "other"


def inspect_notes_snapshot(
    label: str,
    notes: str,
    reference_date: dt.date,
    max_age_proposed: int = 90,
    max_age_terminal: int = 180,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    """Inspect a match_node's `data.notes` for a `Status:` snapshot.

    Returns `(snapshot_info, format_errors, staleness_warnings)`.
    Both `proposed` and terminal states (`enacted`, `in_force`, `died`) are
    checked for age against their respective cadence thresholds.
    """
    if not notes:
        return None, [], []

    m_status = STATUS_PREFIX_RE.search(notes)
    m_date = VERIFIED_DATE_RE.search(notes)

    if not m_status and not m_date:
        return None, [], []

    errors: list[str] = []
    stale: list[str] = []

    if m_status and not m_date:
        errors.append(
            f"{label}: has 'Status:' in data.notes but is missing 'verified as of YYYY-MM-DD'"
        )
        return None, errors, stale

    if m_date and not m_status:
        errors.append(
            f"{label}: has 'verified as of {m_date.group(1)}' in data.notes but does not start the status clause with 'Status:'"
        )
        return None, errors, stale

    assert m_status is not None and m_date is not None
    date_str = m_date.group(1)
    try:
        verified_date = dt.date.fromisoformat(date_str)
    except ValueError:
        errors.append(f"{label}: invalid calendar date in 'verified as of {date_str}'")
        return None, errors, stale

    status_body = m_status.group("body").strip()
    category = classify_status_state(status_body)
    if category == "other":
        errors.append(
            f"{label}: unrecognized status state after 'Status:' ({status_body[:60]!r}); "
            "expected Proposed, Enacted, In force, or Died on the Order Paper"
        )
        return None, errors, stale

    age_days = (reference_date - verified_date).days
    threshold = max_age_proposed if category == "proposed" else max_age_terminal
    if age_days > threshold:
        stale.append(
            f"{label}: status snapshot ({category}) verified {date_str} is {age_days} days old "
            f"(exceeds {threshold}-day re-verification threshold)"
        )

    info = {
        "label": label,
        "category": category,
        "verified_date": date_str,
        "age_days": age_days,
        "threshold_days": threshold,
        "status_body": status_body,
    }
    return info, errors, stale


def check_legisinfo_payload_against_notes(
    label: str,
    notes: str,
    payload: Any,
) -> list[str]:
    """Compare a live Parliament of Canada LEGISinfo JSON payload against `data.notes`.

    Flags drift when the live bill stage/status has advanced beyond what
    `data.notes` records (e.g., Bill C-34 passing second reading and moving to
    committee while `notes` still says only First Reading).
    """
    mismatches: list[str] = []
    bill = payload[0] if isinstance(payload, list) and payload else payload
    if not isinstance(bill, dict):
        return [f"{label}: unexpected LEGISinfo JSON root type {type(bill).__name__}"]

    status_en = (bill.get("StatusNameEn") or "").strip()
    latest_stage_en = (bill.get("LatestCompletedMajorStageNameWithChamberSuffix") or "").strip()
    is_session_ongoing = bill.get("IsSessionOngoing", True)
    received_royal_assent = bool(bill.get("ReceivedRoyalAssent", False)) or (
        "royal assent" in status_en.lower() or "royal assent" in latest_stage_en.lower()
    )
    did_reinstate = bool(bill.get("DidReinstateInNextSession", False))

    m_clause = STATUS_CLAUSE_RE.search(notes or "")
    if m_clause:
        status_clause = m_clause.group("clause").strip()
    else:
        m_status = STATUS_PREFIX_RE.search(notes or "")
        status_clause = m_status.group("body").strip() if m_status else ""

    category = classify_status_state(status_clause)
    clause_lower = status_clause.lower()

    # If the parliamentary session has ended without Royal Assent or reinstatement,
    # the bill died on the Order Paper regardless of the stage it was in when the session ended.
    if is_session_ongoing is False and not received_royal_assent and not did_reinstate:
        if category != "died" and "will not proceed" not in clause_lower:
            mismatches.append(
                f"{label}: LEGISinfo reports IsSessionOngoing=False, ReceivedRoyalAssent=False "
                f"(stage at dissolution={status_en!r}) but Status clause ({status_clause!r}) does not record that the bill died on the Order Paper"
            )
        return mismatches

    # Check key progression milestones against the parsed Status clause (never trailing prose)
    if received_royal_assent:
        if category not in ("enacted", "in_force"):
            mismatches.append(
                f"{label}: LEGISinfo reports Royal Assent (StatusNameEn={status_en!r}, "
                f"LatestStage={latest_stage_en!r}) but Status clause has category={category!r} ({status_clause!r})"
            )
        return mismatches

    if "will not proceed" in status_en.lower():
        if category != "died" and "will not proceed" not in clause_lower:
            mismatches.append(
                f"{label}: LEGISinfo reports StatusNameEn={status_en!r} "
                f"but Status clause ({status_clause!r}) does not record that the bill died on the Order Paper / will not proceed"
            )
        return mismatches

    if category != "proposed":
        mismatches.append(
            f"{label}: LEGISinfo reports active bill (StatusNameEn={status_en!r}) "
            f"but Status clause has non-proposed category={category!r} ({status_clause!r})"
        )

    if "consideration in committee" in status_en.lower():
        if "committee" not in clause_lower:
            mismatches.append(
                f"{label}: LEGISinfo reports StatusNameEn={status_en!r} "
                f"(LatestStage={latest_stage_en!r}) but Status clause does not mention committee stage"
            )

    if "second reading" in latest_stage_en.lower():
        if "second reading" not in clause_lower:
            mismatches.append(
                f"{label}: LEGISinfo reports LatestCompletedMajorStage={latest_stage_en!r} "
                f"but Status clause does not mention second reading"
            )

    if "third reading" in latest_stage_en.lower():
        if "third reading" not in clause_lower:
            mismatches.append(
                f"{label}: LEGISinfo reports LatestCompletedMajorStage={latest_stage_en!r} "
                f"but Status clause does not mention third reading"
            )

    return mismatches


def scan_regulation_registry(
    reference_date: dt.date,
    max_age_proposed: int = 90,
    max_age_terminal: int = 180,
) -> tuple[list[dict[str, Any]], list[str], list[str], list[tuple[str, str, str]], int]:
    """Scan all `registry/regulation/**/*.json` files.

    Returns `(snapshots, format_errors, stale_warnings, legisinfo_targets, unstamped_count)`.
    """
    snapshots: list[dict[str, Any]] = []
    format_errors: list[str] = []
    stale_warnings: list[str] = []
    legisinfo_targets: list[tuple[str, str, str]] = []
    unstamped_count = 0

    for path in sorted(glob.glob(REGULATION_GLOB, recursive=True)):
        rel = os.path.relpath(path, REPO_ROOT)
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        ns = doc.get("namespace", "?")
        for idx, mn in enumerate(doc.get("match_nodes") or []):
            data = mn.get("data") or {}
            cname = (
                data.get("canonical_name")
                or ((mn.get("patterns") or [f"node[{idx}]"])[0].strip("^$").replace("(?i)", ""))
            )
            label = f"{rel} (secid:regulation/{ns}/{cname})"
            notes = data.get("notes") or ""
            info, errs, stale = inspect_notes_snapshot(
                label,
                notes,
                reference_date=reference_date,
                max_age_proposed=max_age_proposed,
                max_age_terminal=max_age_terminal,
            )
            format_errors.extend(errs)
            stale_warnings.extend(stale)
            if info is not None:
                snapshots.append(info)
            elif not errs:
                unstamped_count += 1

            for u in data.get("urls") or []:
                url = u.get("url") if isinstance(u, dict) else None
                if isinstance(url, str) and LEGISINFO_JSON_RE.match(url):
                    legisinfo_targets.append((label, url, notes))

    return snapshots, format_errors, stale_warnings, legisinfo_targets, unstamped_count


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        resolved = urllib.parse.urljoin(req.full_url, newurl)
        if not effective_url_is_safe(resolved):
            raise urllib.error.URLError(f"redirect to unsafe URL blocked: {resolved}")
        return super().redirect_request(req, fp, code, msg, headers, resolved)


def run_live_checks(legisinfo_targets: list[tuple[str, str, str]], timeout: float = 15.0) -> list[str]:
    """Query live machine-readable legislative status endpoints and return any mismatches."""
    failures: list[str] = []
    opener = urllib.request.build_opener(_SafeRedirectHandler)
    headers = {
        "User-Agent": "SecID-Regulation-Status-Check/1.0 (+https://secid.cloudsecurityalliance.org)",
        "Accept": "application/json",
    }
    for label, url, notes in legisinfo_targets:
        if not effective_url_is_safe(url):
            failures.append(f"{label}: SSRF guard blocked {url}")
            continue
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with opener.open(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if status >= 400:
                    failures.append(f"{label}: HTTP {status} fetching {url}")
                    continue
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            failures.append(f"{label}: error fetching {url}: {exc}")
            continue

        mismatches = check_legisinfo_payload_against_notes(label, notes, payload)
        failures.extend(mismatches)

    return failures


def run_self_tests() -> int:
    today = dt.date(2026, 11, 4)

    # 1. Valid proposed snapshot within 90 days
    info, errs, stale = inspect_notes_snapshot(
        "test:proposed-fresh",
        "Status: Proposed — At consideration in committee in the House of Commons (verified as of 2026-11-04).",
        reference_date=today,
    )
    assert not errs and not stale and info and info["category"] == "proposed", (info, errs, stale)

    # 2. Valid terminal snapshots (Enacted, In force, Died on the Order Paper)
    for notes_sample, expected_cat in [
        ("Status: Enacted (Royal Assent June 15, 2026; verified as of 2026-11-04).", "enacted"),
        ("Status: In force (commenced January 23, 2022; verified as of 2026-11-03).", "in_force"),
        ("Status: Died on the Order Paper (44th Parliament; verified as of 2026-11-04).", "died"),
    ]:
        info, errs, stale = inspect_notes_snapshot("test:terminal", notes_sample, reference_date=today)
        assert not errs and not stale and info and info["category"] == expected_cat, (info, errs, stale)

    # 3. Missing 'verified as of YYYY-MM-DD' on a Status: note must fail
    info, errs, stale = inspect_notes_snapshot(
        "test:missing-date",
        "Status: proposed, pre-second-reading as of this sweep entry (2026).",
        reference_date=today,
    )
    assert info is None and len(errs) == 1 and "missing 'verified as of YYYY-MM-DD'" in errs[0], (info, errs)

    # 4. Invalid calendar date must fail
    info, errs, stale = inspect_notes_snapshot(
        "test:bad-date",
        "Status: Proposed (verified as of 2026-02-30).",
        reference_date=today,
    )
    assert info is None and len(errs) == 1 and "invalid calendar date" in errs[0], (info, errs)

    # 5. Terminal states are NOT exempt from staleness checks (>180 days flagged)
    info, errs, stale = inspect_notes_snapshot(
        "test:stale-enacted",
        "Status: In force (verified as of 2026-01-01).",
        reference_date=today,
        max_age_proposed=90,
        max_age_terminal=180,
    )
    assert not errs and len(stale) == 1 and "exceeds 180-day" in stale[0], (info, errs, stale)

    # 6. Proposed bills have a tighter staleness threshold (>90 days flagged)
    info, errs, stale = inspect_notes_snapshot(
        "test:stale-proposed",
        "Status: Proposed (verified as of 2026-07-01).",
        reference_date=today,
        max_age_proposed=90,
        max_age_terminal=180,
    )
    assert not errs and len(stale) == 1 and "exceeds 90-day" in stale[0], (info, errs, stale)

    # 7. Exact Bill C-34 regression test (#228):
    #    Live LEGISinfo reports committee consideration + second reading completed,
    #    while stale notes only mentioned First Reading.
    c34_live_payload = [
        {
            "NumberCode": "C-34",
            "ParliamentNumber": 45,
            "SessionNumber": 1,
            "StatusNameEn": "At consideration in committee in the House of Commons",
            "LatestCompletedMajorStageNameWithChamberSuffix": "Second reading in the House of Commons",
        }
    ]
    stale_c34_notes = (
        "Status: Proposed (First Reading June 10, 2026 in the 45th Parliament, 1st Session; "
        "Private Member's Bill sponsored by Garnett Genuis; verified as of 2026-11-03)."
    )
    c34_mismatches = check_legisinfo_payload_against_notes("test:bill-c-34-stale", stale_c34_notes, c34_live_payload)
    assert len(c34_mismatches) == 2, f"Expected 2 mismatches (committee + second reading), got: {c34_mismatches}"

    updated_c34_notes = (
        "Status: Proposed — At consideration in committee in the House of Commons; "
        "passed second reading on October 29, 2026 (agreed to on division) and referred to the "
        "Standing Committee on Canadian Heritage (CHPC) (First Reading June 10, 2026 in the "
        "45th Parliament, 1st Session; verified as of 2026-11-04)."
    )
    c34_ok = check_legisinfo_payload_against_notes("test:bill-c-34-updated", updated_c34_notes, c34_live_payload)
    assert not c34_ok, f"Expected no mismatches on updated Bill C-34 notes, got: {c34_ok}"

    # 8. Ended parliamentary session without Royal Assent -> died on the Order Paper (e.g., 44-1 Bill C-27 / AIDA)
    c27_live_payload = [
        {
            "NumberCode": "C-27",
            "ParliamentNumber": 44,
            "SessionNumber": 1,
            "IsSessionOngoing": False,
            "ReceivedRoyalAssent": False,
            "DidReinstateInNextSession": False,
            "StatusNameEn": "At consideration in committee in the House of Commons",
            "LatestCompletedMajorStageNameWithChamberSuffix": "Second reading in the House of Commons",
        }
    ]
    c27_stale = check_legisinfo_payload_against_notes(
        "test:bill-c-27-stale",
        "Status: Proposed (At consideration in committee in the House of Commons; verified as of 2024-12-01).",
        c27_live_payload,
    )
    assert len(c27_stale) == 1 and "died on the Order Paper" in c27_stale[0], c27_stale
    c27_ok = check_legisinfo_payload_against_notes(
        "test:bill-c-27-updated",
        "Status: Died on the Order Paper (44th Parliament, 1st Session; verified as of 2026-11-04).",
        c27_live_payload,
    )
    assert not c27_ok, c27_ok

    # 9. Negated / trailing prose ('Not yet in force') on a Proposed bill must NOT mask Royal Assent
    c36_notes_with_negated_in_force = (
        "Status: Proposed — At second reading in the House of Commons; First reading completed June 15, 2026 "
        "in the 45th Parliament, 1st Session (verified as of 2026-11-04). Not yet in force — track alongside "
        "PIPEDA (secid:regulation/priv.gc.ca/pipeda) which remains current law."
    )
    c36_royal_assent_payload = [
        {
            "NumberCode": "C-36",
            "ParliamentNumber": 45,
            "SessionNumber": 1,
            "IsSessionOngoing": True,
            "ReceivedRoyalAssent": True,
            "StatusNameEn": "Royal Assent",
            "LatestCompletedMajorStageNameWithChamberSuffix": "Royal Assent",
        }
    ]
    c36_mismatch = check_legisinfo_payload_against_notes(
        "test:bill-c-36-royal-assent",
        c36_notes_with_negated_in_force,
        c36_royal_assent_payload,
    )
    assert len(c36_mismatch) == 1 and "category='proposed'" in c36_mismatch[0], c36_mismatch

    print("OK: check-regulation-status.py self-tests passed (9/9 cases)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests and exit")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Query live machine-readable legislative APIs (e.g. Parliament of Canada LEGISinfo JSON)",
    )
    parser.add_argument(
        "--fail-on-stale",
        action="store_true",
        help="Exit non-zero if any dated Status: snapshot exceeds its max-age threshold",
    )
    parser.add_argument(
        "--max-age-days-proposed",
        type=int,
        default=90,
        help="Maximum days before a Proposed bill snapshot is flagged for re-verification (default: 90)",
    )
    parser.add_argument(
        "--max-age-days-terminal",
        type=int,
        default=180,
        help="Maximum days before an Enacted / In force / Died snapshot is flagged for re-verification (default: 180)",
    )
    parser.add_argument(
        "--reference-date",
        default=None,
        help="ISO date (YYYY-MM-DD) to measure snapshot age against (default: today UTC)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    ref_date = (
        dt.date.fromisoformat(args.reference_date)
        if args.reference_date
        else dt.datetime.now(dt.timezone.utc).date()
    )

    snapshots, format_errors, stale_warnings, legisinfo_targets, unstamped_count = scan_regulation_registry(
        reference_date=ref_date,
        max_age_proposed=args.max_age_days_proposed,
        max_age_terminal=args.max_age_days_terminal,
    )

    by_category: dict[str, int] = {}
    for s in snapshots:
        cat = s["category"]
        by_category[cat] = by_category.get(cat, 0) + 1

    if format_errors:
        print(f"FAIL: {len(format_errors)} malformed regulation Status snapshot(s):", file=sys.stderr)
        for err in format_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(snapshots)} dated regulation Status snapshot(s) valid "
        f"(proposed={by_category.get('proposed', 0)}, "
        f"enacted={by_category.get('enacted', 0)}, "
        f"in_force={by_category.get('in_force', 0)}, "
        f"died={by_category.get('died', 0)}; "
        f"{unstamped_count} legacy regulation node(s) without Status: clause)"
    )

    if stale_warnings:
        stream = sys.stderr if args.fail_on_stale else sys.stdout
        prefix = "FAIL" if args.fail_on_stale else "WARN"
        print(f"{prefix}: {len(stale_warnings)} snapshot(s) due for re-verification:", file=stream)
        for w in stale_warnings:
            print(f"  - {w}", file=stream)
        if args.fail_on_stale:
            return 1

    if args.live:
        live_failures = run_live_checks(legisinfo_targets)
        if live_failures:
            print(
                f"FAIL: {len(live_failures)} live legislative status mismatch(es) across "
                f"{len(legisinfo_targets)} endpoint(s):",
                file=sys.stderr,
            )
            for failure in live_failures:
                print(f"  - {failure}", file=sys.stderr)
            return 1
        print(
            f"OK: {len(legisinfo_targets)} live machine-readable legislative endpoint(s) match registry Status snapshots"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
