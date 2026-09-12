"""Verify every declared model/window, artifact hash, saved metric and summary."""

from pulsegraph.cli import review_main

if __name__ == "__main__":
    review_main("integrity")
