#ifndef TipPredict_Data_hpp
#define TipPredict_Data_hpp

#include <fstream>
#include <vector>

namespace TipPredict
{

// An object of this class represents a dataset, which (at this time)
// is the supports for a single claim.
class Data
{
    private:

        // Times and amounts of the tips
        std::vector<double> times;
        std::vector<double> amounts;

    public:

        // Constructor. Provide the filename where the data is to be read from
        Data(const char* filename);
};


/* IMPLEMENTATIONS FOLLOW */

Data::Data(const char* filename)
{
    // Read in the data
    std::fstream fin(filename, std::ios::in);
    double x, y;
    while(fin >> x && fin >> y)
    {
        times.push_back(x);
        amounts.push_back(y);
    }
    fin.close();
}

} // namespace

#endif

