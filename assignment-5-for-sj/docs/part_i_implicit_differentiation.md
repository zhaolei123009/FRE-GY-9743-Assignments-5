# Part I: Implicit Function Differentiation

## Q1. Recovering model inputs from market observations

Write the model inputs as $x=X^I\in\mathbb{R}^n$, market observations as
$m=X^M\in\mathbb{R}^n$, and define the residual

$$F(x,m)=V(x)-m.$$

We seek a root $F(x,m)=0$. Start from a reasonable initial guess, calculate the
residual and the Jacobian $J(x)=\partial V/\partial x$, and solve

$$J(x_k)\Delta x_k=-F(x_k,m),\qquad x_{k+1}=x_k+\lambda_k\Delta x_k.$$

A damped Newton method uses a line search to choose $0<\lambda_k\leq1$ so that
the residual decreases and parameter constraints remain satisfied. Solve the
linear system rather than explicitly forming an inverse. Stop when the pricing
residual is below a chosen tolerance, while also monitoring step size and
conditioning. Analytic derivatives or automatic differentiation are preferable;
finite differences can be used if neither is available.

Alternatively, minimize a weighted squared residual with a constrained nonlinear
least-squares solver. If the final residual is nonzero, this is an approximate
fit, and its sensitivity is obtained from the optimization first-order conditions,
not automatically from the exact-root formula below.

Equal dimensions alone do not guarantee existence or uniqueness. A nonsingular
Jacobian at an exact solution guarantees a locally unique differentiable inverse.
Global uniqueness requires additional structure, a restricted admissible domain,
or a separate argument. Different starting guesses are useful diagnostics but
are not a proof of global uniqueness.

## Q2. Sensitivity of the calibrated inputs

At an exact calibrated solution $x^*(m)$,

$$V(x^*(m))=m.$$

Differentiating gives

$$J(x^*)\,dx^*=dm,\qquad
\frac{\partial X^I}{\partial X^M}=J(x^*)^{-1}.$$

This follows from the implicit function theorem, assuming $V$ is continuously
differentiable and $J(x^*)$ is nonsingular. For a particular quote bump $h$,
solve $J(x^*)s=h$ to obtain the first-order parameter change $s$. For the full
matrix, solve $JA=I$. A poorly conditioned Jacobian amplifies quote noise.

If a downstream scalar value $M(x)$ depends on market observations only through
calibration, then

$$\frac{\partial M}{\partial m}
=\frac{\partial M}{\partial x}J^{-1}.$$

For many quotes and one scalar value, solve the adjoint system
$J^Tz=(\nabla_x M)$; then $z=\nabla_m M$. Direct dependence on $m$ requires
an additional direct derivative term. A singular Jacobian invalidates the local
inverse formula; a pseudoinverse is an additional selection rule, not a unique
inverse sensitivity.

## Q3. Three OTM option prices and an implied-volatility interpolator

### Calibration

Assume the three options have a common expiry $T>0$, known fixed forward $F>0$,
positive strikes, and fixed option types. Use an OTM put for $K_1<F$, an ATM
put or call for $K_2=K_{\rm atm}$, and an OTM call for $K_3>F$.
The quotes are **undiscounted**, so use an undiscounted pricing function;
there is no discount factor to insert into the calibration equations.
For a Black forward-price convention,

$$B_c(F,K,\sigma,T)=F\Phi(d_1)-K\Phi(d_2),$$
$$B_p(F,K,\sigma,T)=K\Phi(-d_2)-F\Phi(-d_1),$$
$$d_1=\frac{\log(F/K)+\tfrac12\sigma^2T}{\sigma\sqrt T},\qquad
 d_2=d_1-\sigma\sqrt T.$$

This convention is an explicit modeling assumption. If the market uses a normal
or shifted-lognormal convention, use that convention consistently instead.

Choose three independent parameters $\theta\in\mathbb{R}^3$ and solve

$$V_i(\theta)=B_i(F,K_i,\sigma(K_i;\theta),T)=P_i,
\qquad i=1,2,3.$$

A useful alternative is to invert each admissible option price to its implied
volatility $s_i$, then fit $\sigma(K_i;\theta)=s_i$. Under Black pricing,
vega is positive for finite positive volatility, so each interior admissible
price has a unique implied volatility. Boundary quotes can yield zero or
unbounded implied volatility and require separate treatment.

For example, choose the three node volatilities themselves as parameters:
$\theta=(s_1,s_2,s_3)$, with an interpolator satisfying
$\sigma(K_i;\theta)=\theta_i$. This gives a unique nodal fit for admissible
interior quotes. A fixed interpolation and extrapolation rule then determines
$\sigma(K)$ elsewhere. More than three unconstrained parameters would generally
be underdetermined by three quotes. For a general three-parameter interpolator,
local uniqueness requires a full-rank pricing Jacobian; global uniqueness must
still be justified. Three fitted prices do not guarantee an arbitrage-free
smile between strikes or outside them.

### Parameter risk and quote risk

Holding $F$, $T$, strikes and option types fixed, define

$$S_{ij}=\frac{\partial\sigma(K_i;\theta)}{\partial\theta_j},
\qquad \nu_i=\frac{\partial B_i}{\partial\sigma}
=F\phi(d_{1,i})\sqrt T.$$

The calibration Jacobian is

$$J_{ij}=\nu_iS_{ij},\qquad J=\operatorname{diag}(\nu_1,\nu_2,\nu_3)S.$$

For a small parameter change, the requested volatility sensitivity is simply

$$d\sigma(K)=g(K)d\theta,\qquad
 g(K)=\left(\frac{\partial\sigma(K;\theta)}{\partial\theta_1},
 \frac{\partial\sigma(K;\theta)}{\partial\theta_2},
 \frac{\partial\sigma(K;\theta)}{\partial\theta_3}\right).$$

Combining this with implicit differentiation also gives the sensitivity to
market **prices**, which is different from sensitivity to the parameters:

$$\frac{\partial\theta}{\partial P}=J^{-1},\qquad
 \frac{\partial\sigma(K)}{\partial P}=g(K)J^{-1}.$$

For a nodal linear interpolator $\sigma(K)=\sum_jw_j(K)\theta_j$,
$g(K)=(w_1,w_2,w_3)$, $S=I$, and
$\partial\sigma(K)/\partial P_i=w_i(K)/\nu_i$.
Small vegas make calibration to price changes unstable. If the forward or quote
coordinates also move, include their derivatives; the expressions above hold
those inputs fixed.

### Trader-friendly parameters

A trader can interpret the parameters as **ATM level, skew and curvature**.
For example, use the fixed-strike node vols and define

$$a=s_2,\qquad r=s_3-s_1,\qquad
 b=\frac{s_1+s_3}{2}-s_2.$$

Then $a$ is the ATM level, $r$ measures the right-minus-left wing difference,
and $b$ measures average wing richness relative to ATM. The inverse is

$$s_1=a+b-r/2,\quad s_2=a,\quad s_3=a+b+r/2.$$

These are analogous to ATM volatility, a risk reversal and a butterfly.
For arbitrary fixed strikes, they are intuitive wing measures; standard market
risk reversals/butterflies often use specified delta conventions and may have
different definitions. The transformation is invertible, so it preserves the
nodal fit while expressing risk in more intuitive directions. A common level
bump shifts all node vols, a skew bump moves the two wings oppositely, and a
curvature bump moves both wings relative to ATM. Positivity and arbitrage
constraints still need to be checked after bumps.
