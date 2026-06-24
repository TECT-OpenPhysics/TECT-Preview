#!/usr/bin/env python3
"""WITHDRAWN 2026-06-23 (operator review). This was a vendored MIMIC of the N-001
backend that (a) re-implemented kinetic_coefficients/scalar symbol rather than importing
the original, and (b) OMITTED the shell-bias term eta_shell*(|k|-q0)^2. Superseded by
codes/foundations/n001_solver/ (byte-identical ORIGINAL sources) imported directly by
a1_kernel_checks.py v1.4, which enforces eta_shell=0 and verifies the FULL solver symbol."""
raise ImportError("actual_n001_pde_backend is WITHDRAWN; use codes/foundations/n001_solver/ (real sources) via a1_kernel_checks.py v1.4")
