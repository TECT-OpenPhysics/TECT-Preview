# R-398 scope note — conditioned-collar Doob martingale and shell influence

R-398 / EXP-001242 introduces a condition-before-estimate decomposition for
the actual finite Q3 split histories.  In the product coordinate basis, let
`p` be the reference Gibbs distribution and `q` the transformed history
distribution.  For an oriented collar filtration `F_r`, the likelihood
`L=q/p` gives `M_r=E_p[L|F_r]`.  The finite calculation checks

`chi2(p,q) = chi2_local + sum_{r>=1} E_p[(M_r-M_(r-1))^2]`,

with every shell term retained as a nonnegative number.  This directly
implements the new route idea: localize before taking a square norm, then
leave only shell influence for a future phase-conditioned or contour estimate.

The primary package covers five `(volume, cutoff)` systems, beta in
`{1/2,1}`, two source supports, both source signs, both split orders, both
history signs, every split prefix, both history adjoints and both collar
orientations.  There are 3,584 oriented contexts.  Primary, independent,
hostile, integrated and Lean results are saved under the R-398 run
directories.  The largest identity residual is `1.0570971181733668e-18`;
the largest local `Q2` is `1.0000033752914241`; the largest global chi-square
is `0.0002191742093816259`; the largest unweighted shell cost is
`0.00021579891795778293`; and the largest `mu=1/8` weighted shell cost is
`0.00031475936144631414`.  Every finite shell cost is nonnegative.

These numbers are finite calibration only.  They do not prove a
phase-conditioned influence contraction, a folded Keldysh-to-Euclidean
domination, a cutoff/source/volume/shape-uniform shell bound, a common form
core, common alpha, OS/KMS/GNS reconstruction, a mass gap, continuum, C6,
Sector-A or Pre-A closure.  The next analytic obligation is a uniform
weighted shell square-function estimate on a Hamiltonian-derived common core,
with phase-label terms controlled explicitly.
