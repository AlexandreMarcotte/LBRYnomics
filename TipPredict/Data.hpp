#ifndef TipPredict_Data_hpp
#define TipPredict_Data_hpp

#include <cassert>
#include <fstream>
#include <vector>
#include "yaml-cpp/yaml.h"

namespace TipPredict
{

// An object of this class represents a dataset, which (at this time)
// is the supports for a single claim.
class Data
{
    private:

        // Time interval
        double t_start, t_end, duration;

        // Times and amounts of the tips
        std::vector<double> times;
        std::vector<double> amounts;
        std::vector<double> log_amounts;

        // Number of tips
        int num_tips;

    public:

        // Construct empty data
        Data();

        // Constructor. Provide the filename where the data is to be read from
        Data(const char* filename);

        // Getters
        double get_t_start() const { return t_start; }
        double get_t_end() const { return t_end; }
        double get_duration() const { return duration; }
        const std::vector<double>& get_times() const { return times; }
        const std::vector<double>& get_amounts() const { return amounts; }
        const std::vector<double>& get_log_amounts() const { return log_amounts; }
        int get_num_tips() const { return num_tips; }
};


/* IMPLEMENTATIONS FOLLOW */

Data::Data()
:num_tips(0)
{

}

Data::Data(const char* filename)
{
    std::cout << "# Loading data from " << filename << "..." << std::flush;

    // Load stuff from the YAML file
    YAML::Node yaml;
    try
    {
        yaml = YAML::LoadFile(filename);
    }
    catch(...)
    {
        std::cerr << "Failed to open or parse " << filename << '.' << std::endl;
        return;
    }

    // Extract data from YAML::Node object
    t_start = yaml["t_start"].as<double>();
    t_end = yaml["t_end"].as<double>();

    // Check data integrity
    assert(t_end > t_start);
    assert(yaml["times"].size() == yaml["amounts"].size());
    duration = t_end - t_start;

    // Extract more
    num_tips = yaml["times"].size();
    times.resize(num_tips);
    amounts.resize(num_tips);
    log_amounts.resize(num_tips);
    for(int i=0; i<num_tips; ++i)
    {
        times[i] = yaml["times"][i].as<double>();
        if(i != 0)
            assert(times[i] >= times[i-1]);

        amounts[i] = yaml["amounts"][i].as<double>();
        assert(amounts[i] > 0.0);
        log_amounts[i] = log(amounts[i]);
    }

    std::cout << "done. Found " << num_tips << " tips." << std::endl;
}

} // namespace

#endif

