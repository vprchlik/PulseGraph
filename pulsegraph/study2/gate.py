"""Separate fail-closed Study 2 approval, provenance and registration gate."""

import re
import subprocess
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.study2.constants import (
    CALENDARS,
    ENDPOINT,
    FREEZE_AT,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    STUDY3_DOMAIN,
    STUDY3_FALLBACK_DOMAIN,
    STUDY3_FILES,
    STUDY3_HEADING,
    STUDY3_INVENTORY_SHA256,
    STUDY3_PANEL_DEADLINE,
    STUDY3_PROTOCOL_SHA256,
    STUDY3_SEEDS,
    STUDY3_VARIANTS,
    VARIANTS,
)
from pulsegraph.study2.declarations import PACKAGES_AUTHORITY, validate, validate_study3
from pulsegraph.study2.holdout import (
    evidence_file,
    prepare_plan,
    timestamp,
    utc_now,
    verify_predictions,
)

ADDITION_HEADING = (
    "## Lapses of September 2026 and the families of the October 2026 paper"
    " — dated addition, 2026-10-12"
)
NPM_PANEL_STATUS = "study/study2/npm_panel_status.json"
# A readiness panel names its frozen files; after the target pull it also names the signals
# and the completeness document of that pull, always together.
PANEL_ENTRIES = ("manifest", "selection", "context")
TARGET_ENTRIES = ("signals", "completeness")
# Study 3's single domain panel. An event-enumerated NYC 311 panel also names the per-day census
# its context was counted from; its status file is committed by the panel stage.
STUDY3_PANEL_ENTRIES = {
    STUDY3_DOMAIN: (*PANEL_ENTRIES, "census"),
    STUDY3_FALLBACK_DOMAIN: PANEL_ENTRIES,
}
STUDY3_PANEL_STATUS = "study/study3/{domain}_panel_status.json"


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL)


def source_hashes(root=ROOT_DIR):
    files = {root / "PROTOCOL.md", root / "pyproject.toml"}
    for directory in ("pulsegraph", "scripts", "tests", "study"):
        files.update(
            p
            for p in (root / directory).rglob("*")
            if p.is_file() and p.suffix in (".py", ".json", ".sql") and "__pycache__" not in p.parts
        )
    return {p.relative_to(root).as_posix(): file_hash(p) for p in sorted(files)}


def verify_registration(implementation_commit, *, root=ROOT_DIR):
    if not isinstance(implementation_commit, str) or not re.fullmatch(
        r"[0-9a-f]{40}", implementation_commit
    ):
        raise ValueError("Full implementation commit required")
    if git(root, "rev-parse", "HEAD").decode().strip() != implementation_commit:
        raise ValueError("Implementation commit must be current HEAD")
    blob = git(root, "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
    if sha256_bytes(blob) != PROTOCOL_SHA256 or not (root / "PROTOCOL.md").read_bytes().startswith(
        blob
    ):
        raise ValueError("Study 2 registration bytes changed")
    if git(
        root,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        "PROTOCOL.md",
        "pyproject.toml",
        "pulsegraph",
        "scripts",
        "tests",
        "study",
    ).strip():
        raise ValueError("Study 2 implementation and declarations must be committed and clean")
    return source_hashes(root)


def _approval(document, action, now):
    if (
        document.get("action") != action
        or document.get("confirmed") is not True
        or not document.get("approved_by")
        or not document.get("approved_at")
    ):
        raise ValueError("Separate signed author approval is required")
    if timestamp(document["approved_at"]) > now:
        raise ValueError("Approval is dated in the future")
    if action == "study3":
        # Bound to the Study 3 addition: the commit that added it and the protocol it added.
        if (
            not re.fullmatch(r"[0-9a-f]{40}", str(document.get("addition_commit")))
            or document.get("protocol_sha256") != STUDY3_PROTOCOL_SHA256
        ):
            raise ValueError("Approval is not bound to the Study 3 addition")
        return
    if (
        document.get("protocol_commit") != PROTOCOL_COMMIT
        or document.get("protocol_sha256") != PROTOCOL_SHA256
    ):
        raise ValueError("Approval is not bound to Study 2")


def _runtime(approval, *, root=ROOT_DIR, study3=False):
    sources = verify_registration(approval["implementation_commit"], root=root)
    smoke = read_json(evidence_file(approval["smoke"]))
    registration = (
        dict(component="study3", protocol_sha256=STUDY3_PROTOCOL_SHA256)
        if study3
        else dict(protocol_commit=PROTOCOL_COMMIT, protocol_sha256=PROTOCOL_SHA256)
    )
    if (
        smoke.get("passed") is not True
        or smoke.get("data_kind") != "synthetic"
        or smoke.get("implementation_commit") != approval["implementation_commit"]
        or any(smoke.get(key) != value for key, value in registration.items())
        or smoke.get("seeds") != (STUDY3_SEEDS if study3 else SEEDS)
        or smoke.get("variants") != list(STUDY3_VARIANTS if study3 else VARIANTS)
    ):
        raise ValueError("Current implementation GPU smoke required")
    scripts = ("study2_", "study3_") if study3 else ("study2_",)
    for name, digest in sources.items():
        if name.startswith("pulsegraph/study2/") or (
            name.startswith("scripts/") and any(prefix in name for prefix in scripts)
        ):
            if smoke.get("source_sha256", {}).get(name) != digest:
                raise ValueError("Smoke source hashes differ from the current implementation")
    versions = installed_versions()
    for package in (
        "timesfm",
        "statsforecast",
        "torch",
        "chronos-forecasting",
        "scipy",
        "numpy",
        "pandas",
    ):
        if not versions.get(package) or smoke.get("packages", {}).get(package) != versions[package]:
            raise ValueError("Runtime versions differ from smoke evidence")
    if versions["timesfm"] != "3.0.2" or versions["statsforecast"] != "2.1.1":
        raise ValueError("Package pins differ from registration")
    if (
        smoke.get("memory", {}).get("peak_reserved_bytes", float("inf")) >= 8000000000
        or "4070 SUPER" not in smoke.get("hardware", {}).get("gpu_model", "").upper()
    ):
        raise ValueError("Registered GPU/VRAM smoke evidence required")
    resolution = read_json(root / "study/study2/crps_resolution.json")
    if (
        not resolution.get("passed")
        or resolution["crps"]["tolerance"] != 1e-8
        or resolution["crps"]["max_k"] != 1000000
        or resolution["crps"]["maximum_residual_bound"] >= 1e-8
    ):
        raise ValueError("CRPS numerical resolution is missing or failed")
    for name in ("pulsegraph/study2/distributions.py", "pulsegraph/study2/scores.py"):
        if resolution["source_sha256"].get(name) != sources[name]:
            raise ValueError("CRPS implementation changed after resolution smoke")
    return dict(
        implementation_commit=approval["implementation_commit"],
        source_sha256=sources,
        packages=versions,
        smoke_sha256=approval["smoke"]["sha256"],
    )


def _declarations(component, root):
    spec = read_json(root / f"study/study2/{component}_spec.json")
    family = read_json(root / f"study/study2/{component}_comparisons.json")
    validate(spec, family)
    return spec, family


def verify_addition(*, root=ROOT_DIR):
    """The dated addition of 2026-10-12 must be committed, unedited, in the protocol at HEAD."""
    commit = PACKAGES_AUTHORITY["commit"]
    added = git(root, "show", f"{commit}:PROTOCOL.md")
    current = git(root, "show", "HEAD:PROTOCOL.md")
    try:
        git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    except subprocess.CalledProcessError:
        raise ValueError("The dated addition of 2026-10-12 is not in the history of HEAD") from None
    if (
        ADDITION_HEADING.encode() not in added
        or not current.startswith(added)
        or (root / "PROTOCOL.md").read_bytes() != current
    ):
        raise ValueError("The protocol at HEAD does not carry the dated addition of 2026-10-12")
    return dict(
        addition="PROTOCOL.md, dated addition of 2026-10-12, items 1 and 3",
        addition_commit=commit,
        addition_protocol_sha256=sha256_bytes(added),
        protocol_sha256_at_head=sha256_bytes(current),
    )


def packages_readiness(document, *, root=ROOT_DIR, now=None):
    """The packages-only external readiness of the dated addition of 2026-10-12.

    Item 1: with the holdout not run, no holdout freeze, prediction commit or prediction
    verification precedes external evaluation. Item 3: the family is E01 to E18, so the
    readiness names the one packages panel, npm's frozen achieved panel, and nothing else.
    Target exposure stays separately approved.
    """
    now = utc_now() if now is None else now
    _approval(document, "external_packages", now)
    if document.get("target_access_approved") is not True:
        raise ValueError("External target exposure must be approved separately")
    if set(document.get("panels", {})) != {"packages"}:
        raise ValueError("The packages component takes the packages panel alone")
    if document.get("package_domain") != "npm":
        raise ValueError("The packages component runs on the frozen npm panel")
    frozen = read_json(root / NPM_PANEL_STATUS)["panel"]
    panel = document["panels"]["packages"]
    for name in PANEL_ENTRIES:
        entry = panel.get(name) or {}
        if entry.get("sha256") != frozen[name]["sha256"]:
            raise ValueError("Readiness names a panel other than the frozen npm panel")
        evidence_file(entry)
    if set(panel) - set(PANEL_ENTRIES + TARGET_ENTRIES):
        raise ValueError("The packages panel names an unregistered entry")
    if set(panel) & set(TARGET_ENTRIES):
        target_completeness(panel, CALENDARS["npm"], root=root)
    return panel


def verify_study3_addition(commit, *, root=ROOT_DIR):
    """The dated addition of 2026-10-16 (item 7) and the two declarations committed with it.

    `commit` is the one the signed readiness names. It must be in the history of HEAD and be the
    commit that added the Study 3 heading (its parent's protocol does not carry it); its protocol
    must be the one whose SHA-256 both declaration files record, extended by the protocol at HEAD;
    and both declaration files must be at HEAD and on disk exactly as that commit holds them.
    """
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("The readiness must name the full commit of the Study 3 addition")
    try:
        git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    except subprocess.CalledProcessError:
        raise ValueError("The Study 3 addition is not in the history of HEAD") from None
    heading = STUDY3_HEADING.encode()
    added = git(root, "show", f"{commit}:PROTOCOL.md")
    current = git(root, "show", "HEAD:PROTOCOL.md")
    if (
        sha256_bytes(added) != STUDY3_PROTOCOL_SHA256
        or added.count(heading) != 1
        or not current.startswith(added)
        or (root / "PROTOCOL.md").read_bytes() != current
    ):
        raise ValueError("The protocol at HEAD does not carry the Study 3 addition as registered")
    try:
        before = git(root, "show", f"{commit}^:PROTOCOL.md")
    except subprocess.CalledProcessError:
        before = b""
    if heading in before:
        raise ValueError("The named commit is not the commit that added Study 3")
    declarations = {}
    for name in STUDY3_FILES:
        try:
            committed = git(root, "show", f"{commit}:{name}")
            at_head = git(root, "show", f"HEAD:{name}")
        except subprocess.CalledProcessError:
            raise ValueError(
                "The Study 3 declarations were not committed with the addition"
            ) from None
        if committed != at_head or (root / name).read_bytes() != committed:
            raise ValueError("The Study 3 declarations differ from those of the addition's commit")
        declarations[name] = sha256_bytes(committed)
    return dict(
        addition="PROTOCOL.md, dated addition of 2026-10-16, item 7",
        addition_commit=commit,
        addition_protocol_sha256=sha256_bytes(added),
        protocol_sha256_at_head=sha256_bytes(current),
        declaration_sha256=declarations,
    )


def study3_readiness(document, *, root=ROOT_DIR, now=None):
    """The single-domain readiness of Study 3 (PROTOCOL.md, dated addition of 2026-10-16, item 7).

    One panel: NYC 311's frozen achieved panel, or PyPI only with the predeclared fallback record
    (an operational reason with its evidence, declared before any target scoring). The panel's
    files are those its committed status file names, its manifest was selected with Study 3's
    selection seed, and an NYC 311 panel was verified by the panel deadline. Target exposure is
    approved separately, and target signals enter only with the completeness document of their pull.
    """
    now = utc_now() if now is None else now
    _approval(document, "study3", now)
    if document.get("target_access_approved") is not True:
        raise ValueError("Study 3 target exposure must be approved separately")
    domain = document.get("domain")
    if domain not in STUDY3_PANEL_ENTRIES or set(document.get("panels", {})) != {domain}:
        raise ValueError("The study3 component takes one panel: nyc311, or pypi as its fallback")
    if domain == STUDY3_FALLBACK_DOMAIN:
        fallback = document.get("nyc311_fallback") or {}
        try:
            declared = timestamp(fallback["declared_at"])
        except (AttributeError, KeyError, TypeError, ValueError):
            declared = None
        if (
            not str(fallback.get("reason") or "").strip()
            or fallback.get("declared_before_scoring") is not True
            or not fallback.get("evidence")
            or declared is None
            or declared > now
        ):
            raise ValueError("Predeclared NYC 311 operational failure required")
        for entry in fallback["evidence"]:
            evidence_file(entry)
    entries = STUDY3_PANEL_ENTRIES[domain]
    frozen = read_json(root / STUDY3_PANEL_STATUS.format(domain=domain))["panel"]
    panel = document["panels"][domain]
    for name in entries:
        entry = panel.get(name) or {}
        if entry.get("sha256") != frozen[name]["sha256"]:
            raise ValueError("Readiness names a panel other than the frozen Study 3 panel")
        evidence_file(entry)
    if set(panel) - set(entries + TARGET_ENTRIES):
        raise ValueError("The Study 3 panel names an unregistered entry")
    manifest = read_json(evidence_file(panel["manifest"]))
    if (
        manifest.get("domain") != domain
        or manifest.get("report", {}).get("selection_seed") != STUDY3_SEEDS["selection"]
    ):
        raise ValueError("The panel was not selected with Study 3's selection seed")
    if domain == STUDY3_DOMAIN:
        if manifest.get("inventory_sha256") != STUDY3_INVENTORY_SHA256:
            raise ValueError("The NYC 311 panel was not drawn from the registered 2024 inventory")
        if timestamp(manifest["verified_at"]) > STUDY3_PANEL_DEADLINE:
            raise ValueError("The NYC 311 panel was verified after the Study 3 panel deadline")
    if set(panel) & set(TARGET_ENTRIES):
        target_completeness(panel, CALENDARS[domain], root=root)
    return panel


def authorize_study3(readiness_path, *, root=ROOT_DIR, now=None):
    """Study 3's gate: Study 2's requirements with Study 3's binding, seeds, variants and family."""
    now = utc_now() if now is None else now
    document = read_json(readiness_path)
    study3_readiness(document, root=root, now=now)
    spec, family = (read_json(root / name) for name in STUDY3_FILES)
    validate_study3(spec, family)
    if (
        document.get("estimated_seconds", 0) <= 0
        or document.get("runtime_budget_seconds", 0) < document["estimated_seconds"]
    ):
        raise ValueError("Runtime budget approval required")
    if document.get("source_semantics_resolved") is not True or not document.get("evidence"):
        raise ValueError("Source and implementation readiness evidence is incomplete")
    for entry in document["evidence"]:
        evidence_file(entry)
    metadata = _runtime(document, root=root, study3=True)
    metadata["authority"] = verify_study3_addition(document["addition_commit"], root=root)
    return dict(readiness=document, spec=spec, family=family, metadata=metadata)


def target_completeness(panel, calendar, *, root=ROOT_DIR):
    """The target signals of one readiness panel, bound to the completeness document of their pull.

    The signals a run scores must be the ones the pull verified: the document is verified on the
    domain calendar, names these signals' hash and the panel's manifest and context, ends no
    earlier than the registered endpoint, and every response capture it lists is present at its
    hash (capture paths are relative to the repository root, as the capture client writes them).
    """
    if not panel.get("signals") or not panel.get("completeness"):
        raise ValueError("Target signals require the completeness document of their pull")
    signals = evidence_file(panel["signals"])
    document = read_json(evidence_file(panel["completeness"]))
    if not calendar or document.get("verified") is not True or document.get("calendar") != calendar:
        raise ValueError("Target completeness is not verified on the domain calendar")
    if document.get("signals_sha256") != file_hash(signals):
        raise ValueError("Completeness evidence belongs to different signals")
    if (
        document.get("manifest_sha256") != panel["manifest"]["sha256"]
        or document.get("context_sha256") != panel["context"]["sha256"]
    ):
        raise ValueError("Completeness evidence belongs to a different panel")
    try:
        last = date.fromisoformat(document["last_complete_day"])
        verified = timestamp(document["verified_at"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Completeness evidence needs its last complete day and time") from None
    if last < date.fromisoformat(ENDPOINT):
        raise ValueError("Target signals end before the registered endpoint")
    if last >= verified.astimezone(ZoneInfo(calendar)).date():
        raise ValueError("Last complete day is not fully elapsed at verification")
    captures = document.get("response_evidence")
    if not isinstance(captures, list) or not captures:
        raise ValueError("Completeness evidence lists no response captures")
    for entry in captures:
        try:
            path = Path(root) / entry["path"]
            present = path.is_file() and file_hash(path) == entry["sha256"]
        except (KeyError, TypeError):
            present = False
        if not present:
            raise ValueError("A response capture of the target pull is missing or changed")
    return signals, document


def authorize_holdout(plan_path, approval_path, *, root=ROOT_DIR, now=None):
    now = utc_now() if now is None else now
    if now > FREEZE_AT:
        raise ValueError("Holdout freeze deadline has passed")
    if approval_path is None:
        raise ValueError("Author must confirm the freeze plan before forecasting")
    approval, plan = read_json(approval_path), read_json(plan_path)
    _approval(approval, "freeze", now)
    if approval.get("plan_sha256") != file_hash(plan_path):
        raise ValueError("Approval belongs to a different freeze plan")
    if approval.get("smoke", {}).get("sha256") != plan["timing_evidence"]["sha256"]:
        raise ValueError("Reviewed timing evidence must be the approved implementation smoke")
    if timestamp(approval["approved_at"]) < timestamp(plan["prepared_at"]):
        raise ValueError("Approval predates the reviewed freeze plan")
    _declarations("holdout", root)
    current = prepare_plan(
        plan["sources"],
        plan["timing_evidence"],
        npm_unavailable_reason=plan.get("npm_unavailable_reason"),
        now=now,
    )
    if {k: v for k, v in current.items() if k != "prepared_at"} != {
        k: v for k, v in plan.items() if k != "prepared_at"
    }:
        raise ValueError("Freeze plan changed after review")
    if plan["npm_status"] == "pending":
        raise ValueError("npm readiness decision is pending")
    if approval.get("runtime_budget_seconds", 0) < plan["estimated_seconds"]:
        raise ValueError("Runtime estimate exceeds approved budget")
    metadata = _runtime(approval, root=root)
    from pulsegraph.forecast.hardware import configure_gpu

    metadata["hardware"] = configure_gpu()
    metadata["approval_sha256"] = file_hash(approval_path)
    return metadata


def authorize_component(readiness_path, component, *, root=ROOT_DIR, now=None):
    if component == "study3":
        return authorize_study3(readiness_path, root=root, now=now)
    now = utc_now() if now is None else now
    document = read_json(readiness_path)
    _approval(document, component, now)
    if component not in ("external", "external_packages", "synthetic"):
        raise ValueError("Use the separate holdout freeze approval")
    spec, family = _declarations(component, root)
    if (
        document.get("estimated_seconds", 0) <= 0
        or document.get("runtime_budget_seconds", 0) < document["estimated_seconds"]
    ):
        raise ValueError("Runtime budget approval required")
    if document.get("source_semantics_resolved") is not True or not document.get("evidence"):
        raise ValueError("Source and implementation readiness evidence is incomplete")
    for entry in document["evidence"]:
        evidence_file(entry)
    if component == "synthetic":
        from pulsegraph.study2.synthetic import grid_manifest

        if read_json(root / "study/study2/grid_manifest.json") != grid_manifest():
            raise ValueError("Synthetic grid manifest differs from registration")
    if component == "external_packages":
        packages_readiness(document, root=root, now=now)
    if component == "external":
        if document.get("target_access_approved") is not True:
            raise ValueError("External target exposure must be approved separately")
        if set(document.get("panels", {})) != {"packages", "nyc311", "wikipedia"}:
            raise ValueError("All three external domain slots are required")
        if document.get("package_domain") not in ("npm", "pypi"):
            raise ValueError("Invalid package-domain substitution")
        if document["package_domain"] == "pypi":
            fallback = document.get("npm_fallback", {})
            if not fallback.get("reason") or not fallback.get("declared_before_scoring"):
                raise ValueError("Predeclared npm operational failure required")
        freeze_path = evidence_file(document["holdout_freeze"])
        freeze = read_json(freeze_path)
        if freeze.get("status") != "complete":
            raise ValueError("The holdout freeze must complete before external evaluation")
        verify_predictions(freeze_path.parent)
        commit = document.get("prediction_commit", "")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("Prediction commit required before external evaluation")
        relative = freeze_path.resolve().relative_to(root.resolve()).as_posix()
        if sha256_bytes(git(root, "show", f"{commit}:{relative}")) != file_hash(freeze_path):
            raise ValueError("Prediction commit does not preserve the freeze record")
        if timestamp(git(root, "show", "-s", "--format=%cI", commit).decode().strip()) >= timestamp(
            "2026-10-01T00:00:00Z"
        ):
            raise ValueError("Predictions were committed after the first target day")
    metadata = _runtime(document, root=root)
    if component == "external_packages":
        metadata["authority"] = verify_addition(root=root)
    return dict(readiness=document, spec=spec, family=family, metadata=metadata)
