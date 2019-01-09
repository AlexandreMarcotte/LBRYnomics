#include <iostream>
#include "TipPredict/TipPredict.hpp"

int main()
{
    TipPredict::Data data("lbry://raising-money-for-seattle-childrens#a62da1dec0c727a5b8f0581e46d647ac03f2f59d");
    data.use_lbry();

    return 0;
}

