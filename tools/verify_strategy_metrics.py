#!/usr/bin/env python
"""Verify White Box Python metrics from strategy workbook v0.2 are tool-covered.

Reads strategy_metrics_python_v02.json (103 L5 metrics, Python primary/secondary
columns) and checks each row maps to at least one wired tool directory under
tools/. Does not run tools — wiring only.

Exit 0 = OK, 1 = gap(s). Written 3.6-clean.
"""
from __future__ import print_function

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "strategy_metrics_python_v02.json")
TOOLS = os.path.join(ROOT, "tools")

WIRED = {
    "crosshair", "coverage", "pymcdc", "radon", "lizard", "testmon",
    "cognitive-ast", "jscpd", "pylint", "semgrep", "bandit", "pip-audit",
    "cosmic-ray", "beniget", "pydriller", "ruff", "complexipy", "symilar",
    "opengrep", "opengrep-taint", "trivy", "slipcover", "mutmut",
    "diff-cover", "astroid", "pyan3", "vulture", "dulwich", "settrace",
}

TOOL_ALIASES = {
    "crosshair": "crosshair",
    "mccabe": "lizard",
    "coverage.py": "coverage",
    "coveragepy": "coverage",
    "pytest-cov": "coverage",
    "pytest-cov --cov-branch": "coverage",
    "coverage_paths": "coverage",
    "coverage.py + ast paths": "coverage",
    "coverage.py + beniget": "coverage",
    "radon_cc": "radon",
    "radon/lizard": "radon",
    "copydetect": "symilar",
    "flake8": "ruff",
    "pyflakes": "ruff",
    "safety": "pip-audit",
    "all_uses": "beniget",
    "git_churn": "pydriller",
    "semgrep oss\n+\nbandit": "semgrep",
}


def _norm_tool(label):
    if not label:
        return None
    s = label.strip()
    key = re.sub(r"\s+", " ", s.lower())
    if key in TOOL_ALIASES:
        return TOOL_ALIASES[key]
    compact = s.lower().replace("\n", " ")
    if "semgrep" in compact and "bandit" in compact:
        return "semgrep"
    if "crosshair" in compact:
        return "crosshair"
    if "coverage" in compact or "pytest-cov" in compact:
        return "coverage"
    if "mccabe" in compact:
        return "lizard"
    if "beniget" in compact or "all_uses" in compact:
        return "beniget"
    if "churn" in compact:
        return "pydriller"
    if "settrace" in compact or "sys.settrace" in compact:
        return "settrace"
    if "radon" in compact and "lizard" not in compact:
        return "radon"
    if "lizard" in compact:
        return "lizard"
    return s.split()[0].lower()


def main():
    if not os.path.isfile(MANIFEST):
        print("FAIL  missing %s" % MANIFEST)
        return 1
    with open(MANIFEST) as handle:
        payload = json.load(handle)
    expected = payload.get("metric_count", 103)
    metrics = payload.get("metrics") or []
    problems = []
    if payload.get("branch_id") != "PY-168":
        problems.append("branch_id in manifest is not PY-168")
    if len(metrics) != expected:
        problems.append("manifest lists %d metrics, metric_count says %d"
                        % (len(metrics), expected))
    if expected != 103:
        problems.append("workbook White Box Python column expects 103 metrics, not %d"
                        % expected)
    for row in metrics:
        l5 = row.get("l5_metric") or ""
        prim = _norm_tool(row.get("python_primary"))
        sec = _norm_tool(row.get("python_secondary"))
        tools = [t for t in (prim, sec) if t]
        if not tools:
            problems.append("%r has no Python tool column" % l5)
            continue
        if not any(t in WIRED for t in tools):
            problems.append("%r tools %s not in wired roster"
                            % (l5, tools))
    wired_dirs = set(
        n for n in os.listdir(TOOLS)
        if os.path.isdir(os.path.join(TOOLS, n)) and not n.startswith("_")
    )
    if wired_dirs != WIRED:
        extra = wired_dirs - WIRED
        missing = WIRED - wired_dirs
        if extra:
            problems.append("unexpected tool dirs: %s" % ", ".join(sorted(extra)))
        if missing:
            problems.append("missing tool dirs: %s" % ", ".join(sorted(missing)))

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print("\n%d problem(s)" % len(problems))
        return 1
    print("OK    %d White Box Python metrics covered by %d wired tools"
          % (len(metrics), len(WIRED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
