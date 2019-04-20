#include <iostream>
#include "DNest4/code/Start.h"
#include <string>
#include "TipPredict/TipPredict.hpp"
#include "yaml-cpp/yaml.h"

using namespace TipPredict;

int main(int argc, char** argv)
{
    // Load filename of the dataset to run
    YAML::Node yaml;
    std::string filename;
    try
    {
        yaml = YAML::LoadFile("data.yaml");
        filename = yaml["src"].as<std::string>();
    }
    catch(...)
    {
        std::cerr << "Failed to open or parse data.yaml." << std::endl;
        return -1;
    }

    // Load a dataset and transfer it to where it needs to be
    Data::instance = Data(filename.c_str());

    // Run DNest4
    DNest4::start<MyModel>(argc, argv);

    return 0;
}

