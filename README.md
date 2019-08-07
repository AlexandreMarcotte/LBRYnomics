LBRYnomics
==========

This was initially going to be about Bayesian forecasting of [LBRY](https://api.lbry.io/user/refer?r=9pa98r9uUUFgJ4JpVr1YvH5dMEbXNTvo) tips*
but it's since evolved into an arbitrary collection of Python scripts that do various things like
continuously publishing the stuff at https://www.brendonbrewer.com/lbrynomics.
The forecasting aspect is abandoned until the team stops destroying my assumptions and
things settle into some sort of equilibrium. :-)

(c) 2019 Brendon J. Brewer. LICENCE: MIT.

\* Full disclosure: That's a referral link and
    I'll get a little reward if you install the LBRY app. But so will you.

<!--Dependencies:-->

<!--    * DNest4-->
<!--    * yaml-cpp-->
<!--    * Python 3 and some packages for it like numpy.-->

<!--Model idea:-->

<!--    * Poisson process rate (for whole channel) is a sum of a constant plus-->
<!--      pulses which decay-->
<!--    * Pulses and tips can eventually be marked by the claim. New claims-->
<!--      probably create pulses.-->

<!--Todo list:-->

<!--    * Complexify model (variable poisson rate etc, borrow strength across claims/publishers)-->

