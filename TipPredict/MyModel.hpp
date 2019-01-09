#ifndef TipPredict_MyModel_hpp
#define TipPredict_MyModel_hpp

#include "Data.hpp"
#include <ostream>
#include "DNest4/code/RNG.h"
#include "DNest4/code/Utils.h"

namespace TipPredict
{

// Use a simple Poisson process
class MyModel
{
    private:

        // A dataset
        static Data data;

        // Poisson process rate
        double lambda;

        // Parameters for lognormal tip size
        double mu, sigma;

    public:

        // Basic constructor
        MyModel();

        // The usual DNest4 functions
        void from_prior(DNest4::RNG& rng);
        double perturb(DNest4::RNG& rng);
        double log_likelihood() const;
        void print(std::ostream& out) const;
        std::string description() const;

        // Provide a dataset
        static void transfer_data(Data&& _data);
};

/* IMPLEMENTATIONS FOLLOW */

Data MyModel::data;

MyModel::MyModel()
{

}

void MyModel::from_prior(DNest4::RNG& rng)
{
    lambda = exp(log(1E-4) + log(1E6)*rng.rand());
    mu = exp(rng.randn());
    sigma = 3.0*rng.rand();
}

double MyModel::perturb(DNest4::RNG& rng)
{
    double logH = 0.0;

    int which = rng.rand_int(3);

    if(which == 0)
    {
        lambda = log(lambda);
        lambda += log(1E6)*rng.randh2();
        DNest4::wrap(lambda, log(1E-4), log(1E2));
        lambda = exp(lambda);
    }
    else if(which == 1)
    {
        mu = log(mu);
        logH -= -0.5*pow(mu, 2);
        mu += rng.randh2();
        logH += -0.5*pow(mu, 2);
        mu = exp(mu);
    }
    else
    {
        sigma += 3.0*rng.randh2();
        DNest4::wrap(sigma, 0.0, 3.0);
    }

    return logH;
}

double MyModel::log_likelihood() const
{
    double logL = 0.0;

    for(int i=0; i<data.num_tips-1; ++i)
    {
        // Exponential distribution for gaps
        double gap = data.times[i+1] - data.times[i];

        
    }

    return logL;
}

void MyModel::print(std::ostream& out) const
{
    out << lambda << ' ' << mu << ' ' << sigma;
}

std::string MyModel::description() const
{
    return "lambda, mu, sigma";
}

void MyModel::transfer_data(Data&& _data)
{
    std::swap(data, _data);
}

} // namespace

#endif

