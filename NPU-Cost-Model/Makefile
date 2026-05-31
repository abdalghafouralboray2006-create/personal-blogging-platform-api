CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

TARGET = npu_cost_model

SRCS = main.cpp
OBJS = $(SRCS:.cpp=.o)

HEADERS = hardware.hpp layer.hpp schedule.hpp cost_model.hpp search.hpp roofline.hpp

all: $(TARGET)

$(TARGET): $(OBJS)
$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp $(HEADERS)
$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
rm -f $(OBJS) $(TARGET)

run: $(TARGET)
./$(TARGET)

conv:
./$(TARGET) --layer conv2d

matmul:
./$(TARGET) --layer matmul

debug:
CXXFLAGS = -std=c++17 -O0 -g -Wall -Wextra