# R-382 increasing-cutoff endpoint modular moment stress boundary

R-382 extends the R-381 Gibbs endpoint-energy bridge over an actual-Q3 edge
cutoff sweep d=3,4,5,6 and a V=4 square control at d=2.  All translated
sites, bond terms, both term orders, both time signs, every prefix position and
both history adjoints are included.  The primary lane passes 19,729/19,729
assertions, the independent lane passes 17/17, the integrated verifier passes
130/130, and Lean R382 compiles.

The edge maxima by cutoff are:

* d=3: M_0=2.733031855844076, M_2=0.008378198414559081,
  endpoint=0.004114253036840313;
* d=4: M_0=3.4283208579615874, M_2=0.06491749177608952,
  endpoint=0.022778768600647783;
* d=5: M_0=4.703343964629605, M_2=0.4870620188494611,
  endpoint=0.09831198953294297;
* d=6: M_0=41.64826651661874, M_2=17.719559304500326,
  endpoint=2.153583814589319.

The successive d=5 to d=6 ratios are 8.855033106195243 for M_0 and
36.38049903040583 for M_2.  They trigger the declared finite growth-warning
threshold 1.05.  This is a diagnostic of the finite edge fixture, not a
divergence proof.  The square d=2 control has M_0=0.9999999999999996 and
M_2=1.725572363131804e-30.

The endpoint identity, state-weighted Cauchy envelope, nonnegativity, Gibbs
log-energy relation, per-cutoff coverage and primary/independent agreement
are finite checks.  R382 Lean proves only nonnegative ratio arithmetic and the
logical warning dichotomy.  No source-, volume-, cutoff- or beta-uniform
estimate, common core, common alpha, OS/KMS/GNS dynamics, gap, continuum, C6,
Sector-A or Pre-A conclusion follows.

**Next gate.**  Prove a Hamiltonian-derived common-core estimate for M_0 and
M_2 that either controls this profile or yields a separately named obstruction;
then feed a proved premise into R-380 and the R-377 resolvent telescope.
