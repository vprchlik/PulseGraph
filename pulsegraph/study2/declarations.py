"""Exact registered Study 2 families and component specifications."""

from pulsegraph.study2.constants import (
    BASELINES,
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
    VARIANTS,
)


def comparisons(component):
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
        comparison_count={"external": 54, "synthetic": 6, "holdout": 18}[component],
    )


def validate(spec, family):
    component = spec.get("component")
    if component not in ("external", "synthetic", "holdout"):
        raise ValueError("Unknown Study 2 component")
    if spec != specification(component) or family != comparisons(component):
        raise ValueError("Study 2 declaration differs from the registered specification")
    return component
