#ifndef TipPredict_Data_hpp
#define TipPredict_Data_hpp

#include <string>
#include "lbry/lbryapi.h"

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
    
}

} // namespace

#endif

