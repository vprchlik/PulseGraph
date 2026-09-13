"""The registered pooled-regime comparison family, from saved forecasts only."""

import pandas as pd

from pulsegraph.evaluation.registration import validate_declarations
from pulsegraph.evaluation.reviews import (
    Comparison,
    paired_repository_scores,
    review_cluster_inference,
)


def confirmatory_tables(results, spec, family):
    validate_declarations(spec, family)
    pooled = results.assign(stratum="all")
    comparisons = [Comparison(**item) for item in family["comparisons"]]
    inference = review_cluster_inference(
        pooled,
        comparisons=comparisons,
        declared_count=18,
        metric="qscore9",
        seed=family["bootstrap_seed"],
        n_bootstrap=20000,
        confidence=0.95,
    )
    inference["reject_bh_005"] = inference.wilcoxon_p_bh <= 0.05
    inference["calendar_conditional"] = True
    pairs = []
    for item in comparisons:
        wide = paired_repository_scores(
            pooled[pooled.horizon.eq(item.horizon)],
            model=item.model,
            reference=item.reference,
            metric="qscore9",
        )
        wide = wide.reset_index().rename(
            columns={item.model: "model_score", item.reference: "reference_score"}
        )
        wide["model"], wide["reference"], wide["horizon"] = item.model, item.reference, item.horizon
        wide["difference"] = wide.model_score - wide.reference_score
        pairs.append(wide)
    return inference, pd.concat(pairs, ignore_index=True)
