"""Generate a Shields-compatible JSON badge from a coverage.py JSON report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# These thresholds keep the badge colors intuitive at a glance.
COLOR_STEPS = (
    (95.0, "brightgreen"),
    (90.0, "green"),
    (80.0, "yellowgreen"),
    (70.0, "yellow"),
    (60.0, "orange"),
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the badge generator.

    Returns:
        The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate a Shields-compatible coverage badge JSON file."
    )
    parser.add_argument("coverage_json", help="Path to coverage.py JSON output.")
    parser.add_argument("output_json", help="Path to write the badge JSON file.")
    return parser.parse_args()


def _badge_color(percent: float) -> str:
    """Return a Shields badge color for the reported coverage percentage.

    Args:
        percent: Statement coverage percentage.

    Returns:
        The Shields color name that matches the coverage band.
    """
    for minimum, color in COLOR_STEPS:
        if percent >= minimum:
            return color
    return "red"


def _badge_message(percent: float) -> str:
    """Format the coverage percentage for display in the badge.

    Args:
        percent: Statement coverage percentage.

    Returns:
        A compact badge message such as ``100%`` or ``97.4%``.
    """
    rounded = round(percent, 1)
    if rounded.is_integer():
        return f"{int(rounded)}%"
    return f"{rounded:.1f}%"


def build_badge_payload(coverage_payload: dict[str, object]) -> dict[str, object]:
    """Build a Shields-compatible JSON badge payload from coverage data.

    Args:
        coverage_payload: Parsed coverage.py JSON report.

    Returns:
        A badge payload suitable for ``img.shields.io/endpoint``.
    """
    totals = coverage_payload["totals"]
    if not isinstance(totals, dict):
        raise ValueError("coverage JSON payload is missing a 'totals' object")

    # Use the raw float instead of coverage.py's display field so the badge can
    # show the actual measured percentage rather than a truncated integer.
    percent = float(totals["percent_covered"])
    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": _badge_message(percent),
        "color": _badge_color(percent),
    }


def main() -> int:
    """Generate the badge JSON file from a coverage.py JSON report.

    Returns:
        Process exit code for the badge generation run.
    """
    args = parse_args()
    coverage_path = Path(args.coverage_json)
    output_path = Path(args.output_json)

    coverage_payload = json.loads(coverage_path.read_text(encoding="utf-8"))
    badge_payload = build_badge_payload(coverage_payload)

    # Create the destination directory so CI and local runs behave the same way.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(badge_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
