"""Exact registered Study 2 families and component specifications."""

from pulsegraph.study2.constants import (
    BASELINES,
    CALENDARS,
    CONTEXT_END,
    CONTEXT_START,
    CUTOFFS,
    ENDPOINT,
    FREEZE_AT,
    MODEL_PINS,
    NPM_READY_BY,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    STRATA_START,
    STUDY3_APPENDED_ON,
    STUDY3_DOMAIN,
    STUDY3_FALLBACK_DOMAIN,
    STUDY3_INVENTORY_SHA256,
    STUDY3_MINIMUM_SERIES,
    STUDY3_PANEL_DEADLINE,
    STUDY3_PROTOCOL_SHA256,
    STUDY3_SEEDS,
    STUDY3_STRATA,
    STUDY3_VARIANTS,
    VARIANTS,
)

# PROTOCOL.md, dated addition of 2026-10-12, item 3: the October 2026 paper's external family is
# the packages tests E01 to E18 with one BH correction; E19 to E54 stay whole for a later run.
PACKAGES_AUTHORITY = dict(
    addition="PROTOCOL.md, dated addition of 2026-10-12, item 3",
    commit="8db0d73381e89a61b0ea22e6a8cb2b6e569725c9",
)


def comparisons(component):
    if component == "external_packages":
        family = comparisons("external")
        rows = [row for row in family["comparisons"] if row["domain"] == "packages"]
        return dict(
            family,
            component=component,
            comparison_count=len(rows),
            comparisons=rows,
            authority=PACKAGES_AUTHORITY,
        )
    domains, horizons, prefix = {
        "external": (("packages", "nyc311", "wikipedia"), (7, 30), "E"),
        "synthetic": (("synthetic",), (30,), "S"),
        "holdout": (("github", "npm"), (30,), "H"),
    }[component]
    rows = []
    for domain in domains:
        for model in MODEL_PINS:
            for horizon in horizons:
                pairs = [
                    (model + "_hurdle", model + "_completed"),
                    (model + "_hurdle", "hurdle_count_28"),
                ]
                if component != "synthetic":
                    pairs.append((model + "_raw", "local_mean_28"))
                for variant, reference in pairs:
                    rows.append(
                        dict(
                            id=f"{prefix}{len(rows) + 1:02}",
                            domain=domain,
                            model=variant,
                            reference=reference,
                            horizon=horizon,
                        )
                    )
    return dict(
        component=component,
        protocol_commit=PROTOCOL_COMMIT,
        comparison_count=len(rows),
        comparisons=rows,
        metric="qscore9",
        test="wilcoxon",
        alternative="two-sided",
        method="approx",
        zero_method="wilcox",
        all_zero_p=1.0,
        adjustment="BH",
        q=0.05,
        bootstrap_replicates=20000,
        bootstrap_seed=SEEDS["bootstrap"],
        calendar_conditional=True,
        holdout_npm_unavailable_ids=[f"H{i:02}" for i in range(1, 10)]
        if component == "holdout"
        else [],
    )


def specification(component):
    return dict(
        component=component,
        protocol_commit=PROTOCOL_COMMIT,
        protocol_sha256=PROTOCOL_SHA256,
        seeds=SEEDS,
        variants=list(VARIANTS),
        foundation_models=[
            dict(
                name=n,
                model_id=p[0],
                revision=p[1],
                package_licence="Apache-2.0",
                weight_licence="TimesFM Non-Commercial License v1.0"
                if n == "timesfm3"
                else "Apache-2.0",
            )
            for n, p in MODEL_PINS.items()
        ],
        baselines=list(BASELINES),
        quantile_levels=[i / 10 for i in range(1, 10)],
        package_pins={"timesfm": "3.0.2", "statsforecast": "2.1.1"},
        inference=dict(
            max_context=2048,
            max_horizon=128,
            threads=4,
            batch_size=1,
            device="cuda",
            peak_vram_limit_bytes=8000000000,
        ),
        calendar=dict(
            context_start=CONTEXT_START,
            cutoffs=list(CUTOFFS),
            endpoint=ENDPOINT,
            strata_start=STRATA_START,
            horizons=[7, 30],
            freeze_at=FREEZE_AT.isoformat(),
            npm_ready_by=NPM_READY_BY.isoformat(),
        ),
        completion=dict(
            lower_knot=[0, 0],
            interpolation="linear",
            rounding="floor(Q(U)+0.5)",
            tail="exponential_quantile",
            tail_scale="max(1,q0.9-q0.8)",
            fm_fallback="F0_equals_one_only",
        ),
        count_hurdles=dict(
            lookback=28, occurrence="(n_positive+0.5)/29", minimum_positives=2, fallback="delta_1"
        ),
        dynamic_count=dict(
            implementation="discounted_beta_bernoulli_gamma_poisson",
            discount=0.98,
            initial_parameters=[0.5, 0.5, 0.5, 0.5],
            fallback="hurdle_count_28_if_fewer_than_two_recent_positives",
        ),
        crps=dict(tolerance=1e-8, max_k=1000000, resolution="study/study2/crps_resolution.json"),
        external_package_fallback=dict(
            domain="pypi", deadline="2026-09-28", reason="operational_npm_unavailability_only"
        ),
        aggregation="windows_within_entity_then_equal_entities",
        comparison_count={"external": 54, "external_packages": 18, "synthetic": 6, "holdout": 18}[
            component
        ],
    )


def validate(spec, family):
    component = spec.get("component")
    if component not in ("external", "external_packages", "synthetic", "holdout"):
        raise ValueError("Unknown Study 2 component")
    if spec != specification(component) or family != comparisons(component):
        raise ValueError("Study 2 declaration differs from the registered specification")
    return component


# Study 3, PROTOCOL.md, dated addition of 2026-10-16, item 7. Its two declaration files were
# written with the addition (study/study3/spec.json, study/study3/regime_comparisons.json). The
# values below restate the registration in code, and every field the code acts on must equal them
# exactly. The files' explanatory text is required to be present and is not interpreted; the gate
# binds the files' bytes to the commit that added the addition (gate.verify_study3_addition).
STUDY3_AUTHORITY = dict(
    addition="PROTOCOL.md, dated addition of 2026-10-16, item 7 (Study 3)",
    appended_on_commit=STUDY3_APPENDED_ON,
    commit=None,
    protocol_sha256_with_addition=STUDY3_PROTOCOL_SHA256,
)
STUDY3_STRATUM_BOUNDS = (
    dict(bounds="[0, 0.5)", id="dense", lower=0.0, upper=0.5, upper_inclusive=False),
    dict(bounds="[0.5, 0.9)", id="sparse", lower=0.5, upper=0.9, upper_inclusive=False),
    dict(bounds="[0.9, 1]", id="very_sparse", lower=0.9, upper=1.0, upper_inclusive=True),
)
# The four variants per model as the specification names them. The run keeps Study 2's names for
# the variants Study 2 registered (hurdle_fixed is Study 2's <model>_hurdle) and also saves the raw
# native deciles, the base forecast every variant derives from, which the pooled tables in Study
# 2's form compare with local_mean_28.
STUDY3_REGISTERED_VARIANTS = (
    "completed",
    "hurdle_fixed",
    "hurdle_dynamic",
    "occurrence_model_size_count",
)
STUDY3_RUN_NAMES = dict(hurdle_fixed="hurdle")
STUDY3_FAMILY_SETTINGS = dict(
    adjustment="BH",
    all_zero_p=1.0,
    alternative="two-sided",
    bootstrap_replicates=20000,
    bootstrap_seed=STUDY3_SEEDS["bootstrap"],
    calendar_conditional=True,
    comparison_count=36,
    component="study3",
    method="approx",
    metric="qscore9",
    minimum_complete_series_per_stratum=STUDY3_MINIMUM_SERIES,
    predicted_t1_sign=dict(dense="positive", sparse="negative", very_sparse="negative"),
    protocol_commit=None,
    protocol_sha256=STUDY3_PROTOCOL_SHA256,
    q=0.05,
    test="wilcoxon",
    zero_method="wilcox",
)
# Explanatory text in the two files, by place: present and nonempty, never interpreted.
STUDY3_FAMILY_TEXT = (
    "adjustment_scope",
    "aggregation",
    "bootstrap_interval",
    "contrasts",
    "direction",
    "hypothesis",
    "order",
    "strata_rule",
    "unavailable_rule",
)
STUDY3_SPEC_TEXT = ("base_forecast", "gate", "secondary", "seed_derivation", "variant_definitions")
STUDY3_NESTED_TEXT = dict(
    authority=("commit_note",),
    strata=("selection",),
    primary=("completeness", "counts", "exclusions", "frame", "series_key"),
    fallback=("if_both_fail", "reason", "source"),
)
STUDY3_NESTED = ("authority", "strata", "domain")
STUDY3_FAMILY_NESTED = ("authority", "comparisons", "strata")


def study3_comparisons():
    """R01 to R36 in the addition's order: stratum, model, horizon, contrast (T1, T2)."""
    rows = []
    for stratum in STUDY3_STRATA:
        for model in MODEL_PINS:
            for horizon in (7, 30):
                for contrast, reference in (
                    ("T1", f"{model}_completed"),
                    ("T2", "hurdle_empirical_28"),
                ):
                    rows.append(
                        dict(
                            contrast=contrast,
                            horizon=horizon,
                            id=f"R{len(rows) + 1:02}",
                            model=model,
                            reference=reference,
                            stratum=stratum,
                            variant=f"{model}_hurdle_dynamic",
                        )
                    )
    return rows


def study3_registered_variants():
    return [f"{m}_{v}" for m in MODEL_PINS for v in STUDY3_REGISTERED_VARIANTS] + list(BASELINES)


def study3_run_name(name):
    """The run's saved name of a registered variant (hurdle_fixed is Study 2's <model>_hurdle)."""
    for model in MODEL_PINS:
        for registered, saved in STUDY3_RUN_NAMES.items():
            if name == f"{model}_{registered}":
                return f"{model}_{saved}"
    return name


def study3_specification_values():
    """Every field of study/study3/spec.json that the code acts on, as registered."""
    study2 = specification("external")
    inventory = dict(
        captured_at="2026-09-14T17:08:16+00:00",
        cells=9496,
        frame_year=2024,
        holds_target_period_counts=False,
        path="data/raw/study2/nyc311/inventory.json",
        recognized_board_frame=8469,
        sha256=STUDY3_INVENTORY_SHA256,
    )
    return dict(
        aggregation=study2["aggregation"],
        authority=STUDY3_AUTHORITY,
        baselines=list(BASELINES),
        calendar=dict(
            context_end=CONTEXT_END,
            context_start=CONTEXT_START,
            context_stops_at_cutoff=True,
            cutoffs=list(CUTOFFS),
            endpoint=ENDPOINT,
            horizons=[7, 30],
            panel_deadline=STUDY3_PANEL_DEADLINE.isoformat(),
            strata_start=STRATA_START,
        ),
        comparison_count=36,
        comparisons_file="study/study3/regime_comparisons.json",
        completion=study2["completion"],
        component="study3",
        confirmatory_references=["<model>_completed", "hurdle_empirical_28"],
        confirmatory_variant="hurdle_dynamic",
        count_hurdles=study2["count_hurdles"],
        crps=study2["crps"],
        domain=dict(
            fallback=dict(deadline=STUDY3_PANEL_DEADLINE.isoformat(), name=STUDY3_FALLBACK_DOMAIN),
            primary=dict(
                calendar_timezone=CALENDARS[STUDY3_DOMAIN], inventory=inventory, name=STUDY3_DOMAIN
            ),
        ),
        dynamic_count=study2["dynamic_count"],
        foundation_models=study2["foundation_models"],
        hypothesis_strata=list(STUDY3_STRATA),
        inference=study2["inference"],
        package_pins=study2["package_pins"],
        protocol_commit=None,
        protocol_sha256=STUDY3_PROTOCOL_SHA256,
        quantile_levels=study2["quantile_levels"],
        seeds=STUDY3_SEEDS,
        strata=dict(
            context_inspected=[CONTEXT_START, CONTEXT_END],
            definitions=[dict(row) for row in STUDY3_STRATUM_BOUNDS],
            minimum_complete_series_for_tests=STUDY3_MINIMUM_SERIES,
            per_stratum=100,
            selection_seed=STUDY3_SEEDS["selection"],
            zero_fraction_window=[STRATA_START, CONTEXT_END],
        ),
        study2_registration=dict(protocol_commit=PROTOCOL_COMMIT, protocol_sha256=PROTOCOL_SHA256),
        variants=study3_registered_variants(),
    )


def _text(value):
    """Explanatory text: a nonempty string, or a nonempty list or mapping of them."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        value = list(value.values())
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)


def _matches(declared, registered, text=()):
    """Exactly the registered keys and values, plus the named explanatory text."""
    return (
        isinstance(declared, dict)
        and set(declared) == {*registered, *text}
        and all(declared[key] == value for key, value in registered.items())
        and all(_text(declared[key]) for key in text)
    )


def _outer(document, nested):
    return {k: v for k, v in document.items() if k not in nested}


def validate_study3(spec, family):
    """The committed Study 3 declarations, field by field; any other key or value is refused.

    The comparison rows, every test and adjustment setting, the seeds, the calendar, the strata,
    the variants, the domain and its frozen inventory, and Study 2's models, completion, count
    hurdles, dynamic count, CRPS and inference settings must equal the registration exactly.
    """
    expected = study3_specification_values()
    if not (
        isinstance(spec, dict)
        and set(spec) == {*expected, *STUDY3_SPEC_TEXT}
        and _matches(_outer(spec, STUDY3_NESTED), _outer(expected, STUDY3_NESTED), STUDY3_SPEC_TEXT)
        and _matches(spec["authority"], STUDY3_AUTHORITY, STUDY3_NESTED_TEXT["authority"])
        and _matches(spec["strata"], expected["strata"], STUDY3_NESTED_TEXT["strata"])
        and isinstance(spec["domain"], dict)
        and set(spec["domain"]) == {"primary", "fallback"}
        and all(
            _matches(spec["domain"][part], expected["domain"][part], STUDY3_NESTED_TEXT[part])
            for part in ("primary", "fallback")
        )
    ):
        raise ValueError("Study 3 declaration differs from the registered specification")
    if not (
        isinstance(family, dict)
        and set(family) >= set(STUDY3_FAMILY_NESTED)
        and _matches(
            _outer(family, STUDY3_FAMILY_NESTED), STUDY3_FAMILY_SETTINGS, STUDY3_FAMILY_TEXT
        )
        and _matches(family["authority"], STUDY3_AUTHORITY, STUDY3_NESTED_TEXT["authority"])
        and family["comparisons"] == study3_comparisons()
        and family["strata"] == [dict(row) for row in STUDY3_STRATUM_BOUNDS]
    ):
        raise ValueError("Study 3 declaration differs from the registered family")
    if any(study3_run_name(name) not in STUDY3_VARIANTS for name in spec["variants"]):
        raise ValueError("A registered Study 3 variant is not saved by the run")
    return "study3"
