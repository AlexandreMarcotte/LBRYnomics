TipPredict
==========

Bayesian extrapolation of LBRY tips. This is work in progress and you probably
shouldn't try to use it yet unless you're me.

(c) 2019 Brendon J. Brewer. LICENCE: MIT.

Dependencies:

    * DNest4
    * yaml-cpp

Model idea:

    * Poisson process rate (for whole channel) is a sum of a constant plus
      pulses which decay
    * Pulses and tips can eventually be marked by the claim. New claims
      probably create pulses.

Todo list:

    * Use exported transactions file from LBRY app as data source
    * Complexify model (variable poisson rate etc, borrow strength across claims/publishers)
    * Get data from lbrynet directly instead of the app
