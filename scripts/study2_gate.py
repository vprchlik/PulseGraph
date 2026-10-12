"""Check signed Study 2 readiness without loading models or opening target counts."""

import argparse

from pulsegraph.study2.gate import authorize_component


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=("external", "synthetic"))
    parser.add_argument("--readiness", required=True)
    args = parser.parse_args()
    result = authorize_component(args.readiness, args.component)
    print(
        f"Study 2 {args.component} gate passed: {result['family']['comparison_count']} comparisons"
    )


if __name__ == "__main__":
    main()
