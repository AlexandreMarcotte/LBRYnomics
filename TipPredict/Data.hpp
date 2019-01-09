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
        double publish_time, current_time;

        // Times and amounts of the tips
        std::vector<double> times;
        std::vector<double> amounts;

        // Number of tips
        int num_tips;

    public:

        // Construct empty data
        Data();

        // Constructor. Provide the filename where the data is to be read from
        Data(const char* filename);

        // Give access to MyModel
        friend class MyModel;
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
    publish_time = yaml["publish_time"].as<double>();
    current_time = yaml["current_time"].as<double>();

    // Check data integrity
    assert(current_time > publish_time);
    assert(yaml["times"].size() == yaml["amounts"].size());

    // Extract more
    num_tips = yaml["times"].size();
    times.resize(num_tips);
    amounts.resize(num_tips);
    for(int i=0; i<num_tips; ++i)
    {
        times[i] = yaml["times"][i].as<double>();
        amounts[i] = yaml["amounts"][i].as<double>();
    }

    std::cout << "done. Found " << num_tips << " tips." << std::endl;
}

} // namespace

#endif

