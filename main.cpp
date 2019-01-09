#include <iostream>
#include "DNest4/code/Start.h"
#include "TipPredict/TipPredict.hpp"

using namespace TipPredict;

int main(int argc, char** argv)
{
    // Load a dataset and transfer it to where it needs to be
    Data data("example_data.yaml");
    MyModel::transfer_data(std::move(data));

    // Run DNest4
    DNest4::start<MyModel>(argc, argv);

    return 0;
}

