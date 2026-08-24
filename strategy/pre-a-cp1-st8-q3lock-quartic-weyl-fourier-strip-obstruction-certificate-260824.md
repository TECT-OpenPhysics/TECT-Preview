# EXP-001056 — quartic onsite obstruction to a positive-strip Weyl-Fourier carrier

## Finding

The fixed-beta OS-mixture route identifies a Weyl-Fourier analytic hierarchy
with an exact bond-kick shear/radius recurrence as one possible carrier. This
checkpoint tests a precise subcandidate: a Weyl-Fourier coefficient density
with a positive exponential moment

\\[
  N_\\rho(f)=\\int_{\\mathbb R}e^{\\rho|k|}|f(k)|\\,dk<\\infty,
  \\qquad \\rho>0.
\\]

For the one-component quartic onsite potential

\\[
  V(q)=\\frac{G}{4}q^4,
  \\qquad W_a=\\exp(-iap/\\hbar),
\\]

the exact potential subflow maps the translation sector to a cubic phase,
up to the sign convention for the adjoint action:

\\[
  \\beta_t^V(W_a)=W_a\\exp\\left(\\frac{it}{\\hbar}
       [V(q+a)-V(q)]\\right),
\\]

\\[
  V(q+a)-V(q)=G\\left(aq^3+\\frac32a^2q^2+a^3q+\\frac14a^4\\right).
\\]

Put \\(\\kappa=Gta/\\hbar\\ne0\\). If the resulting coefficient had a
finite positive exponential Fourier moment, its Fourier inversion would
extend it to a bounded holomorphic function on every narrower strip

\\[
  |\\operatorname{Im}z|<\\rho.
\\]

But for \\(z=x+iy\\), the cubic phase satisfies

\\[
  \\operatorname{Im}P(z)=3\\kappa x^2y+O(|x|),
\\]

so choosing \\(y\\kappa<0\\) gives
\\(
|\\exp(iP(x+iy))|=\\exp(-\\operatorname{Im}P(x+iy))
\\) growing like \\(\\exp(3|\\kappa||y|x^2)\\). It is therefore unbounded in
every nonzero strip. This contradicts the weighted-Fourier implication.

The exact fixture uses \\(G=51/35\\), \\(a=1/2\\), \\(t=1/3\\),
\\(\\hbar=1\\), giving \\(\\kappa=17/70\\). Primary and independent
lanes both pass 20/20; the integrated lane passes 31/31 and Lean R238
passes.

## Scope

This retires only the positive-strip L1 Weyl-Fourier density/strip carrier
for the quartic onsite subflow. It is not a no-go theorem for quartic Q3
dynamics. Radius-free Frechet scales, Gevrey or subexponential weights,
modular/state-weighted classes, direct projected \\(D,\\delta D\\) estimates,
and a different Hamiltonian-derived common algebra remain open. The full Q3
Hamiltonian, thermodynamic common alpha, KMS identification, GNS gap,
continuum, C6, Sector A, Pre-A and TECT production owner are untouched.

## Adversarial review

- **Potential-only scope:** only the exact quartic multiplication subflow is
  used; no full Q3 dynamics is inferred. **UPHELD**
- **Carrier definition:** the tested class is exactly positive-strip L1
  Weyl-Fourier, not every analytic or state-weighted class. **UPHELD**
- **Strip implication:** finite exponential moment implies bounded holomorphic
  extension on narrower strips by absolute Fourier inversion. **UPHELD**
- **Growth sign:** the exact cubic coefficient and the choice \\(y\\kappa<0\\)
  give positive quadratic growth in \\( -\\operatorname{Im}P\\). **UPHELD**
- **Radius alternatives:** no conclusion is drawn about zero-radius, Gevrey
  or subexponential profiles. **UPHELD**
- **Lean:** R238 checks rational coefficient and sign fixtures only, not the
  Fourier theorem or unbounded domains. **UPHELD**
- **QFT promotion:** no KMS, common alpha, GNS gap, continuum, C6, Sector A
  or Pre-A result follows. **UPHELD**
- **TECT owner:** no `heat_root_incidence` or A1/R-192 production owner is
  supplied. **UPHELD**

## Next gate

Retain the direct projected \\(D,\\delta D\\) route and test a radius-free
or Gevrey/state-weighted orbit topology inside the fixed-beta OS mixture
envelope. Any surviving candidate must still be identified with the exact
finite-volume Hamiltonian exhaustion before it can yield a common QFT alpha.
