# Q3LOCK local Q2 capped-Gibbs-kernel boundary

R-373 retains the exact theta-half Gibbs difference as the saturating kernel

```text
kappa_beta(Delta)=(2/beta)tanh(beta Delta/2),
0 <= kappa_beta(Delta) <= min(Delta,2/beta).
```

For the centered moved witness, the shell is the symmetric row form

```text
N_(1/2)^2 = 2 sum_i p_i sum_j kappa_beta(Delta_ij)|X_ij|^2,
```

and is bounded by the same expression with `kappa` replaced by its cap.  This
unifies the R-370 low/high transition-energy split and the R-371 Gibbs
variance reduction without assuming a uniform bond spectral gap.

Primary and independent R-373 each pass 17001/17001 assertions over 2816
all-prefix contexts; integrated passes 115/115 and Lean R373 passes.  The
maximum exact identity residual is 2.776e-17, the cap envelope has zero
positive violation, and the maximum capped shell is 1.4610968881346746 with
row form 1.5463623505129311.  Edge maxima at d=3,4,5,6 are
0.008029308807322853, 0.040206939213245196, 0.1172316154764435 and
1.4610968881346746.

This remains finite proxy evidence only.  Source/volume/cutoff-uniform
capped-form control, common core, common alpha, global KMS, OS/KMS/GNS
dynamics, gap, continuum, C6, Sector-A and Pre-A remain open.  No PDF is
issued at this checkpoint.
