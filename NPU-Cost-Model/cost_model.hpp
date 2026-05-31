#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string>

#include "hardware.hpp"
#include "layer.hpp"
#include "schedule.hpp"

struct CostResult {
    long long compute_cycles = 0;
    long long memory_cycles = 0;
    long long total_cycles = 0;

    long long dram_read_bytes = 0;
    long long dram_write_bytes = 0;

    long long tile_sram_bytes = 0;

    double arithmetic_intensity = 0.0;

    bool fits_l1 = false;
    bool fits_l2 = false;

    std::string schedule_name;
};

class CostModel {
public:
    explicit CostModel(const HardwareConfig& hw)
        : hw_(hw) {}

    CostResult evaluate(
        const Conv2DSpec& layer,
        const Conv2DSchedule& sched) const
    {
        CostResult result;

        result.schedule_name = sched.name();

        compute_conv_tile_memory(layer, sched, result);
        compute_conv_dram_traffic(layer, sched, result);
        compute_cycles(
            layer.total_macs(),
            layer.output_elements(),
            layer.fused_activation,
            result);

        return result;
    }

    CostResult evaluate(
        const MatMulSpec& layer,
        const MatMulSchedule& sched) const
    {
        CostResult result;

        result.schedule_name = sched.name();

        compute_matmul_tile_memory(layer, sched, result);
        compute_matmul_dram_traffic(layer, sched, result);
        compute_cycles(
            layer.total_macs(),
            layer.output_elements(),
            layer.fused_activation,
            result);

        return result;
    }

private:
    HardwareConfig hw_;

    static long long ceil_div(long long a, long long b) {
        return (a + b - 1) / b;
    }

    void compute_conv_tile_memory(
        const Conv2DSpec& layer,
        const Conv2DSchedule& sched,
        CostResult& result) const
    {
        const int B = hw_.bytes_per_element;

        int ih =
            sched.toh * layer.stride +
            layer.kernel_h - 1;

        int iw =
            sched.tow * layer.stride +
            layer.kernel_w - 1;

        long long weights =
            static_cast<long long>(sched.toc)
            * sched.tic
            * layer.kernel_h
            * layer.kernel_w
            * B;

        long long input =
            static_cast<long long>(layer.batch)
            * sched.tic
            * ih
            * iw
            * B;

        long long output =
            static_cast<long long>(layer.batch)
            * sched.toc
            * sched.toh
            * sched.tow
            * B;

        result.tile_sram_bytes =
            weights + input + output;

        result.fits_l1 =
            result.tile_sram_bytes <= hw_.l1_sram_bytes;

        result.fits_l2 =
            result.tile_sram_bytes <= hw_.l2_sram_bytes;
    }

    void compute_matmul_tile_memory(
        const MatMulSpec& layer,
        const MatMulSchedule& sched,
        CostResult& result) const
    {
        const int B = hw_.bytes_per_element;

        long long A =
            static_cast<long long>(sched.tm)
            * sched.tk
            * B;

        long long Bm =
            static_cast<long long>(sched.tk)
            * sched.tn
            * B;

        long long C =
            static_cast<long long>(sched.tm)
            * sched.tn
            * B;

        result.tile_sram_bytes =
            A + Bm + C;

        result.fits_l1 =
            result.tile_sram_bytes <= hw_.l1_sram_bytes;

        result.fits_l2 =
            result.tile_sram_bytes <= hw_.l2_sram_bytes;
    }

    void compute_conv_dram_traffic(
        const Conv2DSpec& layer,
        const Conv2DSchedule& sched,
        CostResult& result) const
    {
        const int B = hw_.bytes_per_element;

        long long weights =
            layer.weight_elements() * B;

        long long input =
            layer.input_elements() * B;

        long long output =
            layer.output_elements() * B;

        if (result.fits_l2) {
            result.dram_read_bytes =
                weights + input;

            result.dram_write_bytes =
                output;

            return;
        }

        long long n_oc =
            ceil_div(layer.out_channels,
                     sched.toc);

        long long n_oh =
            ceil_div(layer.output_height(),
                     sched.toh);

        long long n_ow =
            ceil_div(layer.output_width(),
                     sched.tow);

        switch (sched.dataflow) {
        case Dataflow::WeightStationary:

            result.dram_read_bytes =
                weights +
                n_oc * input;

            break;

        case Dataflow::OutputStationary:

            result.dram_read_bytes =
                input +
                (n_oh * n_ow) * weights;

            break;

        case Dataflow::InputStationary:

            result.dram_read_bytes =
                input +
                n_oc * weights;

            break;

        case Dataflow::AllCached:

            result.dram_read_bytes =
                weights + input;

            break;
        }

        result.dram_write_bytes =
            output;
    }

    void compute_matmul_dram_traffic(
        const MatMulSpec& layer,
        const MatMulSchedule& sched,
        CostResult& result) const
    {
        const int B = hw_.bytes_per_element;

        long long A =
            layer.a_elements() * B;

        long long Bm =
            layer.b_elements() * B;

        long long C =
            layer.c_elements() * B;

        if (result.fits_l2) {
            result.dram_read_bytes =
                A + Bm;

            result.dram_write_bytes =
                C;

            return;
        }

        long long n_m =
            ceil_div(layer.M, sched.tm);

        long long n_n =
            ceil_div(layer.N, sched.tn);

        switch (sched.dataflow) {
        case Dataflow::WeightStationary:

            result.dram_read_bytes =
                A + n_m * Bm;

            break;

        case Dataflow::OutputStationary:

            result.dram_read_bytes =
                n_n * A + Bm;

            break;

        case Dataflow::InputStationary:

            result.dram_read_bytes =
                A + Bm;

            break;

        case Dataflow::AllCached:

            result.dram_read_bytes =
                A + Bm;

            break;
        }

        result.dram_write_bytes =
            C;
    }

    void compute_cycles(
        long long total_macs,
        long long output_elements,
        bool fused_activation,
        CostResult& result) const
    {
        double peak_macs =
            hw_.peak_compute_macs_per_cycle();

        result.compute_cycles =
            static_cast<long long>(
                std::ceil(
                    total_macs / peak_macs));

        long long systolic_fill =
            hw_.systolic_rows +
            hw_.systolic_cols;

        result.compute_cycles +=
            systolic_fill;

        if (fused_activation) {
            long long vpu_cycles =
                static_cast<long long>(
                    std::ceil(
                        static_cast<double>(
                            output_elements)
                        /
                        hw_.vpu_elements_per_cycle));

            result.compute_cycles +=
                vpu_cycles;
        }

        long long total_dram =
            result.dram_read_bytes +
            result.dram_write_bytes;

        result.memory_cycles =
            static_cast<long long>(
                std::ceil(
                    static_cast<double>(
                        total_dram)
                    /
                    hw_.dram_bandwidth_bytes_per_cycle));

        result.total_cycles =
            std::max(
                result.compute_cycles,
                result.memory_cycles);

        result.arithmetic_intensity =
            total_dram > 0
            ? (2.0 * total_macs)
                / static_cast<double>(total_dram)
            : 0.0;
    }
};