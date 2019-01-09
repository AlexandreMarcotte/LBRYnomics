#ifndef TipPredict_MyModel_hpp
#define TipPredict_MyModel_hpp

#include "Data.hpp"
#include <iomanip>
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

        // A throwaway RNG just for forecasts
        static DNest4::RNG junk_rng;

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
DNest4::RNG MyModel::junk_rng(0);

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

    // Try to be super fast
    double inv_lambda = 1.0/lambda;
    double log_lambda = log(lambda);

    for(int i=1; i<data.num_tips; ++i)
    {
        // Exponential distribution for gaps
        double gap = data.times[i] - data.times[i-1];
        logL += log_lambda - gap*lambda;
    }

    // No tip between last tip and end of interval
    logL += -(data.current_time - data.times.back())*inv_lambda;

    // Now do the tip amounts
    double C = -0.5*log(2.0*M_PI) - log(sigma);
    double tau = pow(sigma, -2);
    double log_mu = log(mu);
    for(int i=0; i<data.num_tips; ++i)
    {
        logL += C - data.log_amounts[i]
                        - 0.5*tau*pow(data.log_amounts[i] - log_mu, 2);
    }

    return logL;
}

void MyModel::print(std::ostream& out) const
{
    out << std::setprecision(16);
    out << lambda << ' ' << mu << ' ' << sigma << ' ';

    // Forecast total tips over next time interval of length 'duration'
    double expected_num_tips = lambda*data.duration;

    // Simulate from poisson. This method is expensive for large numbers of
    // tips.
    if(expected_num_tips > 1000000)
    {
        std::cerr << "# Warning in MyModel::print(std::ostream&) const.";
        std::cerr << std::endl;
    }

    double t = data.current_time;
    double forecast = 0.0;
    while(true)
    {
        t = t - log(1.0 - junk_rng.rand())/lambda;
        if(t > data.current_time + data.duration)
            break;
        forecast += mu*exp(sigma*junk_rng.randn());
    }

    out << forecast;
}

std::string MyModel::description() const
{
    return "lambda, mu, sigma, forecast";
}

void MyModel::transfer_data(Data&& _data)
{
    std::swap(data, _data);
}

} // namespace

#endif

