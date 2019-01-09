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

        // Construct empty data
        Data();

        // Constructor. Provide the filename where the data is to be read from
        Data(const char* filename);
};


/* IMPLEMENTATIONS FOLLOW */

Data::Data()
{

}

Data::Data(const char* filename)
{
    std::cout << "# Loading data from " << filename << "..." << std::flush;

    // Read in the data
    std::fstream fin(filename, std::ios::in);
    if(!fin)
    {
        std::cerr << "Failed to open file." << std::endl;
        return;
    }

    double x, y;
    while(fin >> x && fin >> y)
    {
        times.push_back(x);
        amounts.push_back(y);
    }
    fin.close();

    std::cout << "done. Found " << times.size() << " tips." << std::endl;
}

} // namespace

#endif

