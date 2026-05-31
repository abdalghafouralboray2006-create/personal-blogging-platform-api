#pragma once

#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <algorithm>

#include "hardware.hpp"
#include "cost_model.hpp"

enum class RooflineRegion {
    MemoryBound,
    ComputeBound
};

struct RooflineResult {
    double peak_compute = 0.0;       // MACs/cycle
    double peak_bandwidth = 0.0;     // bytes/cycle

    double ridge_point = 0.0;        // MACs/byte
    double arithmetic_intensity = 0.0;

    double compute_utilization = 0.0;
    double bandwidth_utilization = 0.0;

    RooflineRegion region = RooflineRegion::MemoryBound;
};

class RooflineAnalyzer {
public:
    static RooflineResult analyze(
        const HardwareConfig& hw,
        const CostResult& result)
    {
        RooflineResult r;

        r.peak_compute =
            hw.peak_compute_macs_per_cycle();

        r.peak_bandwidth =
            hw.dram_bandwidth_bytes_per_cycle;

        r.ridge_point =
            r.peak_compute /
            r.peak_bandwidth;

        r.arithmetic_intensity =
            result.arithmetic_intensity;

        if (r.arithmetic_intensity < r.ridge_point)
        {
            r.region =
                RooflineRegion::MemoryBound;

            r.compute_utilization =
                (r.arithmetic_intensity /
                 r.ridge_point) * 100.0;

            r.bandwidth_utilization = 100.0;
        }
        else
        {
            r.region =
                RooflineRegion::ComputeBound;

            r.compute_utilization = 100.0;

            r.bandwidth_utilization =
                (r.ridge_point /
                 r.arithmetic_intensity) * 100.0;
        }

        return r;
    }

    static void print(
        const HardwareConfig& hw,
        const CostResult& cost)
    {
        auto r = analyze(hw, cost);

        std::cout << "\n";
        std::cout << "==================================================\n";
        std::cout << "Roofline Analysis\n";
        std::cout << "==================================================\n";

        std::cout << std::fixed
                  << std::setprecision(2);

        std::cout
            << "Peak Compute            : "
            << r.peak_compute
            << " MACs/cycle\n";

        std::cout
            << "Peak Bandwidth          : "
            << r.peak_bandwidth
            << " B/cycle\n";

        std::cout
            << "Ridge Point             : "
            << r.ridge_point
            << " MACs/byte\n";

        std::cout
            << "Arithmetic Intensity    : "
            << r.arithmetic_intensity
            << " MACs/byte\n";

        std::cout
            << "Region                  : "
            << (r.region ==
                    RooflineRegion::MemoryBound
                    ? "MEMORY-BOUND"
                    : "COMPUTE-BOUND")
            << "\n";

        std::cout
            << "Compute Utilization     : "
            << r.compute_utilization
            << "%\n";

        std::cout
            << "Bandwidth Utilization   : "
            << r.bandwidth_utilization
            << "%\n";

        print_ascii_chart(r);
    }

private:
    static void print_ascii_chart(
        const RooflineResult& r)
    {
        constexpr int WIDTH = 60;

        double min_ai = 0.1;
        double max_ai = 10000.0;

        auto position =
            [&](double ai)
        {
            double log_min =
                std::log10(min_ai);

            double log_max =
                std::log10(max_ai);

            double log_ai =
                std::log10(
                    std::max(ai, min_ai));

            double t =
                (log_ai - log_min) /
                (log_max - log_min);

            return std::clamp(
                static_cast<int>(t * WIDTH),
                0,
                WIDTH - 1);
        };

        std::vector<char> line(
            WIDTH,
            '-');

        int ridge_pos =
            position(r.ridge_point);

        int ai_pos =
            position(
                r.arithmetic_intensity);

        for (int i = 0;
             i < ridge_pos;
             ++i)
        {
            line[i] = '~';
        }

        for (int i = ridge_pos;
             i < WIDTH;
             ++i)
        {
            line[i] = '=';
        }

        line[ai_pos] = 'O';

        std::cout << "\n";
        std::cout
            << "0.1        1        10       100      1000     10000\n";
        std::cout << "|";

        for (char c : line)
            std::cout << c;

        std::cout << "|\n";

        std::cout
            << "~~~ Memory Bound ~~~"
            << "=== Compute Bound ===\n";

        std::cout
            << "O = Current Operator\n";
    }
};

inline void print_cost_summary(
    const CostResult& r)
{
    std::cout << "\n";
    std::cout
        << "==================================================\n";
    std::cout
        << "Cost Summary\n";
    std::cout
        << "==================================================\n";

    std::cout
        << "Schedule               : "
        << r.schedule_name
        << "\n";

    std::cout
        << "Tile SRAM              : "
        << r.tile_sram_bytes / 1024.0
        << " KB\n";

    std::cout
        << "Fits L1                : "
        << (r.fits_l1 ? "Yes" : "No")
        << "\n";

    std::cout
        << "Fits L2                : "
        << (r.fits_l2 ? "Yes" : "No")
        << "\n";

    std::cout
        << "DRAM Read              : "
        << r.dram_read_bytes / 1024.0
        << " KB\n";

    std::cout
        << "DRAM Write             : "
        << r.dram_write_bytes / 1024.0
        << " KB\n";

    std::cout
        << "Compute Cycles         : "
        << r.compute_cycles
        << "\n";

    std::cout
        << "Memory Cycles          : "
        << r.memory_cycles
        << "\n";

    std::cout
        << "Total Cycles           : "
        << r.total_cycles
        << "\n";

    std::cout
        << "Arithmetic Intensity   : "
        << r.arithmetic_intensity
        << " MACs/byte\n";
}