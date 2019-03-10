#ifndef TipPredict_DataFetcher_hpp
#define TipPredict_DataFetcher_hpp

#include "lbry/lbryapi.h"
#include <string>

namespace TipPredict
{

class DataFetcher
{
    private:
        std::string channel_name;

    public:
        DataFetcher(std::string _channel_name);

};

/* IMPLEMENTATIONS FOLLOW */
DataFetcher::DataFetcher(std::string _channel_name)
:channel_name(std::move(_channel_name))
{

}

} // namespace

#endif

