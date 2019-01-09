#ifndef TipPredict_Data_hpp
#define TipPredict_Data_hpp

#include <fstream>
#include <sstream>
#include <string>
#include <nlohmann/json.hpp>

// Shorthand
using json = nlohmann::json;

namespace TipPredict
{

// An object of this class represents a dataset, which (at this time)
// is the supports for a single claim.
class Data
{
    private:

        // The URL of the claim being investigated.
        std::string url;

    public:

        // Constructor. Provide the URL
        Data(std::string _url);

        // Use LBRY to do something
        void use_lbry();

};


/* IMPLEMENTATIONS FOLLOW */

Data::Data(std::string _url)
:url(std::move(_url))
{

}

void Data::use_lbry()
{
    // Do a VERY DUMB THING
    std::string command = "/opt/LBRY/resources/static/daemon/lbrynet resolve ";
    command += url;
    command += " > output.json";
    system(command.c_str());

    // Read json file contents into a string
    std::fstream fin("output.json", std::ios::in);
    json claim;
    fin >> claim;
    fin.close();

    // Go inside
    claim = claim[url];

    std::cout << claim["claim"]["supports"] << std::endl;
} 

} // namespace

#endif

