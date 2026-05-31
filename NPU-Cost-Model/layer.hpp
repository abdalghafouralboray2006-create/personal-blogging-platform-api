#pragma once

#include <cstdint>
#include <iostream>
#include <string>

enum class LayerType {
    Conv2D,
    MatMul
};

struct Conv2DSpec {
    int batch      = 1;

    int in_channels = 3;
    int in_height   = 224;
    int in_width    = 224;

    int out_channels = 64;

    int kernel_h = 3;
    int kernel_w = 3;

    int stride = 1;
    int padding = 1;

    bool fused_activation = true;

    int output_height() const {
        return (in_height + 2 * padding - kernel_h) / stride + 1;
    }

    int output_width() const {
        return (in_width + 2 * padding - kernel_w) / stride + 1;
    }

    long long output_elements() const {
        return static_cast<long long>(batch)
             * out_channels
             * output_height()
             * output_width();
    }

    long long weight_elements() const {
        return static_cast<long long>(out_channels)
             * in_channels
             * kernel_h
             * kernel_w;
    }

    long long input_elements() const {
        return static_cast<long long>(batch)
             * in_channels
             * in_height
             * in_width;
    }

    long long total_macs() const {
        return static_cast<long long>(batch)
             * out_channels
             * output_height()
             * output_width()
             * in_channels
             * kernel_h
             * kernel_w;
    }

    void print() const {
        std::cout
            << "Layer Type     : Conv2D\n"
            << "Input          : ["
            << batch << ", "
            << in_channels << ", "
            << in_height << ", "
            << in_width << "]\n"

            << "Weights        : ["
            << out_channels << ", "
            << in_channels << ", "
            << kernel_h << ", "
            << kernel_w << "]\n"

            << "Output         : ["
            << batch << ", "
            << out_channels << ", "
            << output_height() << ", "
            << output_width() << "]\n"

            << "Stride         : "
            << stride << "\n"

            << "Padding        : "
            << padding << "\n"

            << "Total MACs     : "
            << total_macs() << "\n\n";
    }
};

struct MatMulSpec {
    int M = 512;
    int K = 512;
    int N = 512;

    bool fused_activation = true;

    long long output_elements() const {
        return static_cast<long long>(M) * N;
    }

    long long a_elements() const {
        return static_cast<long long>(M) * K;
    }

    long long b_elements() const {
        return static_cast<long long>(K) * N;
    }

    long long c_elements() const {
        return static_cast<long long>(M) * N;
    }

    long long total_macs() const {
        return static_cast<long long>(M)
             * K
             * N;
    }

    void print() const {
        std::cout
            << "Layer Type     : MatMul\n"
            << "A Matrix       : ["
            << M << " x " << K << "]\n"

            << "B Matrix       : ["
            << K << " x " << N << "]\n"

            << "Output Matrix  : ["
            << M << " x " << N << "]\n"

            << "Total MACs     : "
            << total_macs() << "\n\n";
    }
};