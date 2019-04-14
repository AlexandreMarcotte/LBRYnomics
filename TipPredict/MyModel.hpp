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

        // A throwaway RNG just for forecasts
        static DNest4::RNG junk_rng;

        // Constant poisson process rate
        double lambda;

        // Parameters for mixture-of-lognormal tip sizes
        double mu, sigma; // Location of both, scale of wide
        double u, wide_weight;

        // Get instantaneous poisson rate
        double instantaneous_rate(double t) const;

        // Integrate variable poisson process rate between two times
        double integrate_rate(double t0, double t1) const;

    public:

        // Basic constructor
        MyModel();

        // The usual DNest4 functions
        void from_prior(DNest4::RNG& rng);
        double perturb(DNest4::RNG& rng);
        double log_likelihood() const;
        void print(std::ostream& out) const;
        std::string description() const;
};

/* IMPLEMENTATIONS FOLLOW */

DNest4::RNG MyModel::junk_rng(0);

MyModel::MyModel()
{

}

void MyModel::from_prior(DNest4::RNG& rng)
{
    lambda = exp(log(1E-6) + log(1E6)*rng.rand());
    mu = exp(3.0*rng.randn());
    sigma = 0.3 + 4.7*rng.rand();
    u = 0.05 + 0.95*rng.rand();
    wide_weight = rng.rand();
}

double MyModel::perturb(DNest4::RNG& rng)
{
    double logH = 0.0;

    int which = rng.rand_int(5);

    if(which == 0)
    {
        lambda = log(lambda);
        lambda += log(1E6)*rng.randh2();
        DNest4::wrap(lambda, log(1E-6), log(1.0));
        lambda = exp(lambda);
    }
    else if(which == 1)
    {
        mu = log(mu);
        logH -= -0.5*pow(mu/3.0, 2);
        mu += 3.0*rng.randh2();
        logH += -0.5*pow(mu/3.0, 2);
        mu = exp(mu);
    }
    else if(which == 2)
    {
        sigma += 4.7*rng.randh2();
        DNest4::wrap(sigma, 0.3, 5.0);
    }
    else if(which == 3)
    {
        u += 0.95*rng.randh();
        DNest4::wrap(u, 0.05, 1.0);
    }
    else
    {
        wide_weight += rng.randh();
        DNest4::wrap(wide_weight, 0.0, 1.0);
    }

    return logH;
}

double MyModel::log_likelihood() const
{
    double logL = 0.0;

    // Get data
    const auto& times = Data::instance.get_times();
    const auto& log_amounts = Data::instance.get_log_amounts();

    // Beginning of time to first tip
    if(times.size() > 0)
    {
        logL += log(instantaneous_rate(times[0]))
                    - integrate_rate(Data::instance.get_t_start(), times[0]);
    }

    // Inter-tip times
    for(int i=1; i<Data::instance.get_num_tips(); ++i)
    {
        logL += log(instantaneous_rate(times[i]))
                    - integrate_rate(times[i-1], times[i]);
    }

    // No tip between last tip and end of interval
    logL += -integrate_rate((times.size() > 0)?(times.back()):(Data::instance.get_t_start()),
                                Data::instance.get_t_end());

    // Now do the tip amounts
    // 1 = wide, 2 = narrow
    double C1 = -0.5*log(2.0*M_PI) - log(sigma);
    double tau1 = pow(sigma, -2);
    double C2 = -0.5*log(2.0*M_PI) - log(u*sigma);
    double tau2 = pow(u*sigma, -2);
    double log_mu = log(mu);
    double log_wide_weight = log(wide_weight);
    double log_narrow_weight = log(1.0 - wide_weight);

    double logL1, logL2;

    for(int i=0; i<Data::instance.get_num_tips(); ++i)
    {
        logL1 = log_wide_weight + C1 - log_amounts[i]
                        - 0.5*tau1*pow(log_amounts[i] - log_mu, 2);
        logL2 = log_narrow_weight + C2 - log_amounts[i]
                        - 0.5*tau2*pow(log_amounts[i] - log_mu, 2);
        logL += DNest4::logsumexp(logL1, logL2);
    }

    return logL;
}

double MyModel::instantaneous_rate(double t) const
{
    return lambda;
}

double MyModel::integrate_rate(double t0, double t1) const
{
    assert(t0 <= t1);
    return (t1 - t0)*lambda;
}

void MyModel::print(std::ostream& out) const
{
    out << std::setprecision(16);
    out << lambda << ' ' << mu << ' ' << sigma << ' ';
    out << u << ' ' << wide_weight << ' ';

    // Forecast total tips over next month
    static constexpr double prediction_interval = 17532.0;
    double expected_num_tips = integrate_rate
                (Data::instance.get_t_end(),
                 Data::instance.get_t_end() + prediction_interval);

    // Simulate from poisson. This method is expensive for large numbers of
    // tips.
    if(expected_num_tips > 1000000)
    {
        std::cerr << "# Expect slowness in MyModel::print(std::ostream&) const.";
        std::cerr << std::endl;
    }

    double t = Data::instance.get_t_end();
    double forecast = 0.0;
    while(true)
    {
        t = t - log(1.0 - junk_rng.rand())/lambda;
        if(t > Data::instance.get_t_end() + prediction_interval)
            break;

        double s = (junk_rng.rand() <= wide_weight)?
                   (sigma):(u*sigma);

        forecast += mu*exp(s*junk_rng.randn());
    }

    out << forecast;
}

std::string MyModel::description() const
{
    return "lambda, mu, sigma, u, wide_weight, forecast";
}

} // namespace

#endif

