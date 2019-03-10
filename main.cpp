#include <iostream>
#include "DNest4/code/Start.h"
#include "TipPredict/TipPredict.hpp"

using namespace TipPredict;

int main(int argc, char** argv)
{
    // Make a data fetcher
    DataFetcher df("Blog");
    df.execute();

//    // Load a dataset and transfer it to where it needs to be
//    Data::instance = Data("example_data.yaml");

//    // Run DNest4
//    DNest4::start<MyModel>(argc, argv);

    return 0;
}

