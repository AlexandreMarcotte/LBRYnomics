#ifndef TipPredict_MyModel_hpp
#define TipPredict_MyModel_hpp

#include "DNest4/code/RNG.h"

namespace TipPredict
{

// Use a simple Poisson process
class MyModel
{
    private:

        // Poisson process rate
        double lambda;

        // Parameters for lognormal tip size
        double mu, sigma;

    public:

        MyModel();

        void from_prior(DNest4::RNG& rng);

};

/* IMPLEMENTATIONS FOLLOW */

MyModel::MyModel()
{

}

void MyModel::from_prior(DNest4::RNG& rng)
{
    lambda = exp(log(1E-4) + log(1E6)*rng.rand());
    mu = exp(rng.randn());
    sigma = 3.0*rng.rand();
}

} // namespace

#endif

