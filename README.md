TipPredict
==========

Bayesian extrapolation of [LBRY](https://api.lbry.io/user/refer?r=9pa98r9uUUFgJ4JpVr1YvH5dMEbXNTvo) tips*. This is work in progress and you probably
shouldn't try to use it yet unless you're me.

(c) 2019 Brendon J. Brewer. LICENCE: MIT.

\* Full disclosure: That's a referral link and I'll get a little reward if you install the program.

Dependencies:

    * DNest4
    * yaml-cpp
    * Python 3 and some packages for it like numpy.

Model idea:

    * Poisson process rate (for whole channel) is a sum of a constant plus
      pulses which decay
    * Pulses and tips can eventually be marked by the claim. New claims
      probably create pulses.

Todo list:

    * Complexify model (variable poisson rate etc, borrow strength across claims/publishers)

