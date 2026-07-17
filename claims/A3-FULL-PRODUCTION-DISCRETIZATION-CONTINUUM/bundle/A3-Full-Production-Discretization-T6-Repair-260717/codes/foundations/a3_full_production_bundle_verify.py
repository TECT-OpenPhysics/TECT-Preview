#!/usr/bin/env python3
"""Bundle-safe one-command verifier for the repaired P3 conditional theorem.

The repository verifier normally reruns every CPU audit.  A reproduction
bundle already runs those audits as separate entry points, so this final entry
validates their immutable results and the recorded CUDA artifact without
overwriting hardware evidence on a CPU-only referee machine.
"""

from __future__ import annotations

import sys

import a3_full_production_verify

__version__ = "1.1.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]


if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--reuse-recorded-audits"]
    raise SystemExit(a3_full_production_verify.main())
