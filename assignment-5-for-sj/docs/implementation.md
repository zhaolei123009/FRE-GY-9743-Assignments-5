# Implementation and validation

## Mathematical specification

For local IFR nodes $f_j$, let the interpolator's integrated weights be

$$w_j(T)=\frac{\partial}{\partial f_j}\int_0^{t(T)}f(u)\,du.$$

The local discount factor and its derivative are

$$D(T)=\exp\left(-\int_0^{t(T)}f(u)\,du\right),\qquad
\frac{\partial D(T)}{\partial f_j}=-D(T)w_j(T).$$

The code uses the interpolator's integral-gradient method, keeping the derivative
consistent with its piecewise-constant interpolation and flat extrapolation.
The curve clock uses the starter's `accrued` convention (ACT/ACT ISDA by default),
while the sample cashflow uses ACT/360. These are intentionally different clocks.

For a funding component referencing a base component,

$$D_{\rm funding}=D_{\rm spread}D_{\rm base}.$$

Each component receives its own local gradient multiplied by all the other
local discount factors in the reference chain. This product rule extends to
longer chains, avoids division by a zero/underflowed discount factor, and detects
circular references. Component order comes from the model's registered block map.
Unrelated blocks are zero on overwrite and remain unchanged on accumulation.

For the product, $C=N\alpha$ with signed notional $N$ and accrual fraction $\alpha$:

| Payment relative to value date | PV | Cash today | Raw state risk |
|---|---|---|---|
| Future | $CD(T_p)$ | 0 | $C\nabla D(T_p)$ |
| Today | $C$ | $C$ | 0 |
| Past | 0 | 0 | 0 |

The funding parameter is resolved for the product currency. Both a single
funding index and the starter's currency-to-index mapping are supported.

All gradient methods mutate the supplied container and return `None`.
`scaler` applies only to the new contribution. With `accumulate=False`, the
existing result is replaced; with `True`, the new contribution is added.
No 1 bp scaling is applied inside the engine; the reporting layer handles it.

## Verified results

Validation environment: Python 3.11.0, NumPy 1.26.4, pandas 2.3.1, QuantLib 1.41.
The eight unittest methods pass. All 13 original notebook code cells execute
successfully, and the notebook contains their saved outputs.

For the sample inputs, $t_1=90/365$, $t_p=273/365$ and $t_s=181/365$.
The independent closed-form cross-check is

$$D=\exp\{-0.03t_1-0.04(t_p-t_1)-0.001(t_p-t_s)\},$$
$$PV=1{,}000{,}000\times\frac{91}{360}\times D
=245{,}870.91057967892.$$

| Block | Node | Raw derivative | PV change per +1 bp |
|---|---|---:|---:|
| SOFR | 2026-04-02 | -60625.703979 | -6.062570 |
| SOFR | 2027-01-02 | -123272.264756 | -12.327226 |
| SOFR | 2028-01-02 | 0.000000 | 0.000000 |
| Funding spread | 2026-07-02 | -121925.026890 | -12.192503 |
| Funding spread | 2027-01-02 | -61972.941845 | -6.197294 |

The last SOFR node has zero risk because its segment begins after payment.
The risk table is a first-order approximation, not exact finite-bump P&L.

## Test coverage

1. Independent closed-form PV and gradient calculations.
2. Local gradient central differences at time zero, a knot, an interior date,
   and an extrapolated date; overwrite, negative scaling and accumulation.
3. Base-curve and funding-curve gradients against central differences.
4. Product gradients against central differences for positive, negative and zero notionals.
5. Past/today payment PV, cash and zero-risk accumulation behavior.
6. Three-level reference chain differentiation and circular-reference rejection.
7. Currency funding selection and public PV/risk reporting with 1 bp scaling.
8. Rejection of invalid local dates, gradient shapes and integer gradient arrays.

Central differences use an absolute rate step of `1e-6` (0.01 bp). Each original
node value is restored in a `finally` block. Tests compare independent numerical
perturbations with the analytic results rather than reproducing the gradient code.

GitHub Actions is configured to rerun tests and the notebook on pushes/PRs;
no hosted Actions run is claimed before this project is uploaded.
