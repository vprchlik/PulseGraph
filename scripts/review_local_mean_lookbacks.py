"""Report every requested, previously run local-mean lookback without refitting."""

from pulsegraph.cli import review_main

if __name__ == "__main__":
    review_main("local_mean_lookbacks")
