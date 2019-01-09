CXX = g++
FLAGS = -std=c++17
INCLUDE = -I $(DNEST4_PATH)
OPTIM = -O2 -g
WARN = -Wall -Wextra -pedantic
ALL = $(FLAGS) $(INCLUDE) $(OPTIM) $(WARN)

default:
	$(CXX) $(ALL) -c main.cpp
	$(CXX) -pthread -L $(DNEST4_PATH)/DNest4/code -o main main.o -ldnest4 -lpthread
	rm -f main.o


tidy:
	clang-tidy main.cpp -- $(INCLUDE)
