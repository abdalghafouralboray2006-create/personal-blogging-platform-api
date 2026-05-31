#pragma once

#include <string>
#include <sstream>
#include <cstdint>

enum class Dataflow {
    WeightStationary,
    OutputStationary,
    InputStationary,
    AllCached
};

inline std::string to_string(Dataflow d) {
    switch (d) {
        case Dataflow::WeightStationary:
            return "WeightStationary";
        case Dataflow::OutputStationary:
            return "OutputStationary";
        case Dataflow::InputStationary:
            return "InputStationary";
        case Dataflow::AllCached:
            return "AllCached";
    }
    return "Unknown";
}

// =====================================================
// Conv2D Schedule
// =====================================================

struct Conv2DSchedule {
    int toc = 16; // output channel tile
    int tic = 16; // input channel tile

    int toh = 16; // output height tile
    int tow = 16; // output width tile

    Dataflow dataflow = Dataflow::WeightStationary;

    std::string name() const {
        std::ostringstream ss;

        ss << "Conv2D["
           << "toc=" << toc
           << ",tic=" << tic
           << ",toh=" << toh
           << ",tow=" << tow
           << ",df=" << to_string(dataflow)
           << "]";

        return ss.str();
    }
};

// =====================================================
// MatMul Schedule
// =====================================================

struct MatMulSchedule {
    int tm = 64;
    int tn = 64;
    int tk = 64;

    Dataflow dataflow = Dataflow::WeightStationary;

    std::string name() const {
        std::ostringstream ss;

        ss << "MatMul["
           << "tm=" << tm
           << ",tn=" << tn
           << ",tk=" << tk
           << ",df=" << to_string(dataflow)
           << "]";

        return ss.str();
    }
};

// =====================================================
// Schedule Candidate
// =====================================================

struct ScheduleCandidate {
    std::string schedule_name;

    Dataflow dataflow = Dataflow::WeightStationary;

    long long tile_sram_bytes = 0;

    bool fits_l1 = false;
    bool fits_l2 = false;

    ScheduleCandidate() = default;
};

// =====================================================
// Search Space Configuration
// =====================================================

struct SearchConfig {
    bool explore_weight_stationary = true;
    bool explore_output_stationary = true;
    bool explore_input_stationary  = false;

    bool allow_l2_spill = true;

    std::initializer_list<int> conv_channel_tiles {
        8, 16, 32, 64, 128
    };

    std::initializer_list<int> conv_spatial_tiles {
        8, 16, 32, 64
    };

    std::initializer_list<int> matmul_tiles {
        16, 32, 64, 128, 256
    };
};