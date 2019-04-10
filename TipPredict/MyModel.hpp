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

        // Pulses - amplitude hyperparameter in units of lambda
        double pulse_height;

        // Latent N(0, 1) coordinates and the pulse amplitudes
        std::vector<double> ns;
        std::vector<double> As;
        void compute_As();

        // Parameters for lognormal tip size
        double mu, sigma;

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
:ns(Data::instance.get_claim_times().size())
,As(Data::instance.get_claim_times().size())
{

}

void MyModel::compute_As()
{
    for(size_t i=0; i<ns.size(); ++i)
        As[i] = pulse_height*lambda*exp(ns[i]);
}

void MyModel::from_prior(DNest4::RNG& rng)
{
    lambda = exp(log(1E-4) + log(1E6)*rng.rand());
    pulse_height = exp(3.0*rng.randn());
    for(size_t i=0; i<ns.size(); ++i)
        ns[i] = rng.randn();
    compute_As();

    mu = exp(rng.randn());
    sigma = 0.05 + 4.95*rng.rand();
}

double MyModel::perturb(DNest4::RNG& rng)
{
    double logH = 0.0;

    int which = rng.rand_int(6);

    if(which == 0)
    {
        lambda = log(lambda);
        lambda += log(1E6)*rng.randh2();
        DNest4::wrap(lambda, log(1E-4), log(1E2));
        lambda = exp(lambda);
    }
    else if(which == 2)
    {
        pulse_height = log(pulse_height);
        logH -= -0.5*pow(pulse_height/3.0, 2);
        pulse_height += 3.0*rng.randh();
        logH += -0.5*pow(pulse_height/3.0, 2);
        pulse_height = exp(pulse_height);

        compute_As();
    }
    else if(which == 3)
    {
        int k = rng.rand_int(ns.size());

        logH -= -0.5*pow(ns[k], 2);
        ns[k] += rng.randh();
        logH += -0.5*pow(ns[k], 2);

        // This could be made more efficient by only doing element k
        compute_As();
    }
    else if(which == 4)
    {
        mu = log(mu);
        logH -= -0.5*pow(mu, 2);
        mu += rng.randh2();
        logH += -0.5*pow(mu, 2);
        mu = exp(mu);
    }
    else
    {
        sigma += 4.95*rng.randh2();
        DNest4::wrap(sigma, 0.05, 5.0);
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
    logL += log(instantaneous_rate(times[0]))
                    - integrate_rate(Data::instance.get_t_start(), times[0]);

    // Inter-tip times
    for(int i=1; i<Data::instance.get_num_tips(); ++i)
    {
        logL += log(instantaneous_rate(times[i]))
                    - integrate_rate(times[i-1], times[i]);
    }

    // No tip between last tip and end of interval
    logL += -integrate_rate(times.back(), Data::instance.get_t_end());

    // Now do the tip amounts
    double C = -0.5*log(2.0*M_PI) - log(sigma);
    double tau = pow(sigma, -2);
    double log_mu = log(mu);
    for(int i=0; i<Data::instance.get_num_tips(); ++i)
    {
        logL += C - log_amounts[i]
                        - 0.5*tau*pow(log_amounts[i] - log_mu, 2);
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
    out << lambda << ' ' << pulse_height << ' ' << mu << ' ' << sigma << ' ';

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
        forecast += mu*exp(sigma*junk_rng.randn());
    }

    out << forecast;
}

std::string MyModel::description() const
{
    return "lambda, mu, sigma, forecast";
}

} // namespace

#endif

