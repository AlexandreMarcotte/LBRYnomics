#include <iostream>
#include "TipPredict/TipPredict.hpp"

using namespace TipPredict;

int main()
{
    // Load a dataset and transfer it to where it needs to be
    Data data("example_data.yaml");
    MyModel::transfer_data(std::move(data));

    return 0;
}

