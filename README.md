LBRYnomics
==========

This was initially going to be about Bayesian forecasting of LBRY tips,
but it's since evolved into an arbitrary collection of Python scripts that do various things, including continually scraping and publishing data the [LBRYnomics page on LBRY Social](https://lbry.social/lbrynomics).

It's not user friendly and you probably shouldn't try to use it, but if you really want to, [get in touch](https://www.brendonbrewer.com/contact.html). I might be persuaded to make a proper package out of it.

(c) 2019 Brendon J. Brewer. LICENCE: MIT.

While you're here, here is a live-ish (updated about every 10 minutes) plot of the total amount of content on LBRY:

![claims.png](https://brendonbrewer.com/lbrynomics/claims.png)

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

