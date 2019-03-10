CXX = g++
FLAGS = -std=c++17
CPPBRY_PATH = /home/brewer/Projects/CppBRY
INCLUDE = -I $(DNEST4_PATH) -I $(CPPBRY_PATH) -I $(CPPBRY_PATH)/third_party/json/include
OPTIM = -O3 -march=native
WARN = -Wall -Wextra -pedantic
ALL = $(FLAGS) $(INCLUDE) $(OPTIM) $(WARN)

default:
	$(CXX) $(ALL) -c main.cpp
	$(CXX) -pthread -L $(DNEST4_PATH)/DNest4/code -L$(CPPBRY_PATH) -o main main.o -lpthread -lcurl -lcurlpp -lcppbry -ldnest4 -lyaml-cpp
	rm -f main.o


tidy:
	clang-tidy main.cpp -- $(INCLUDE)
