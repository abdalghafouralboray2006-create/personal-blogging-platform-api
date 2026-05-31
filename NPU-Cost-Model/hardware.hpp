#pragma once

#include <iostream>
#include <iomanip>
#include <string>

struct HardwareConfig {
    // Memory hierarchy
    long long l1_sram_bytes = 256LL * 1024;
    long long l2_sram_bytes = 2LL * 1024 * 1024;

    // DRAM
    double dram_bandwidth_bytes_per_cycle = 32.0;

    // Compute array
    int systolic_rows = 16;
    int systolic_cols = 16;

    // Data type
    int bytes_per_element = 2; // FP16

    // Vector unit
    int vpu_elements_per_cycle = 32;

    // Clock
    double frequency_ghz = 1.0;

    // Utilization
    double mac_efficiency = 0.85;

    int macs_per_cycle() const {
        return systolic_rows * systolic_cols;
    }

    double peak_compute_macs_per_cycle() const {
        return macs_per_cycle() * mac_efficiency;
    }

    double peak_compute_gmacs() const {
        return peak_compute_macs_per_cycle() * frequency_ghz;
    }

    std::string dtype_name() const {
        switch (bytes_per_element) {
            case 1: return "INT8";
            case 2: return "FP16";
            case 4: return "FP32";
            default: return "Unknown";
        }
    }

    void print() const {
        std::cout
            << "==================================================\n"
            << "Hardware Configuration\n"
            << "==================================================\n"
            << "L1 SRAM               : "
            << l1_sram_bytes / 1024 << " KB\n"

            << "L2 SRAM               : "
            << l2_sram_bytes / (1024 * 1024) << " MB\n"

            << "DRAM Bandwidth        : "
            << dram_bandwidth_bytes_per_cycle
            << " B/cycle\n"

            << "Systolic Array        : "
            << systolic_rows << " x "
            << systolic_cols << "\n"

            << "MACs/Cycle            : "
            << macs_per_cycle() << "\n"

            << "MAC Efficiency        : "
            << std::fixed
            << std::setprecision(1)
            << mac_efficiency * 100.0
            << "%\n"

            << "Peak Compute          : "
            << peak_compute_macs_per_cycle()
            << " MACs/cycle\n"

            << "VPU Throughput        : "
            << vpu_elements_per_cycle
            << " elems/cycle\n"

            << "Data Type             : "
            << dtype_name()
            << " ("
            << bytes_per_element
            << " B)\n"

            << "Clock Frequency       : "
            << frequency_ghz
            << " GHz\n"

            << "==================================================\n";
    }
};