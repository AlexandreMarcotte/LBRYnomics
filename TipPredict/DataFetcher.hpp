#ifndef TipPredict_DataFetcher_hpp
#define TipPredict_DataFetcher_hpp

#include <algorithm>
#include "lbry/lbryapi.h"
#include <sstream>
#include <string>

using json = nlohmann::json;

namespace TipPredict
{

class DataFetcher
{
    private:
        std::string name;

    public:
        DataFetcher(std::string _name);

        void execute();

};

/* IMPLEMENTATIONS FOLLOW */
DataFetcher::DataFetcher(std::string _name)
:name(std::move(_name))
{

}

void DataFetcher::execute()
{
    json response = lbry::LbrydAPI::call(
                      "claim_list",             // method
                      {{"name", name}}  // param list as a std::map
                    );

    /* This returns a JSON-RPC formatted object in the form
        { 
            "id": "X",          // body values we sent to the API
            "jsonrpc": "2.0",   
            "result": {
                ...
                // this is the actual information  we received from the 
                // API. If something went wrong, instead of getting
                // "result" as the parent member, 
                // we'd instead get "error".
                ... 
            }
         } 
         */

    json supports = response["result"]["claims"][0]["supports"];
    for(const auto& support: supports)
    {
        std::stringstream ss1;
        ss1 << support["amount"];
        std::string s = ss1.str();
        s.erase(std::remove(s.begin(), s.end(), '\"'), s.end());
        std::stringstream ss2;
        ss2 << s;
        double value;
        ss2 >> value;
        std::cout << value << std::endl;
//        std::cout << support << std::endl;
    }
//    std::cout << std::setw(4) << response_data << std::endl;
}

} // namespace

#endif

