#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include "hardware.hpp"
#include "layer.hpp"
#include "schedule.hpp"
#include "cost_model.hpp"
#include "search.hpp"
#include "roofline.hpp"

static bool has_arg(
    const std::vector<std::string>& args,
    const std::string& flag)
{
    return std::find(
        args.begin(),
        args.end(),
        flag) != args.end();
}

static int get_int(
    const std::vector<std::string>& args,
    const std::string& flag,
    int default_value)
{
    for (size_t i = 0; i + 1 < args.size(); ++i)
    {
        if (args[i] == flag)
            return std::stoi(args[i + 1]);
    }

    return default_value;
}

static std::string get_string(
    const std::vector<std::string>& args,
    const std::string& flag,
    const std::string& default_value)
{
    for (size_t i = 0; i + 1 < args.size(); ++i)
    {
        if (args[i] == flag)
            return args[i + 1];
    }

    return default_value;
}

static void print_usage(const char* prog)
{
    std::cout
        << "\nNPU Cost Model\n\n"

        << "Usage:\n"
        << "  " << prog << " --layer conv2d\n"
        << "  " << prog << " --layer matmul\n\n"

        << "Conv2D:\n"
        << "  --batch N\n"
        << "  --in_c C\n"
        << "  --in_h H\n"
        << "  --in_w W\n"
        << "  --out_c C\n"
        << "  --kernel K\n"
        << "  --stride S\n"
        << "  --pad P\n\n"

        << "MatMul:\n"
        << "  --M value\n"
        << "  --K value\n"
        << "  --N value\n\n"

        << "General:\n"
        << "  --top N\n"
        << "  --help\n\n";
}

static void print_top_results(
    const std::vector<CostResult>& results)
{
    if (results.empty())
        return;

    std::cout
        << "\n==================================================\n"
        << "Top Candidates\n"
        << "==================================================\n";

    for (size_t i = 0; i < results.size(); ++i)
    {
        const auto& r = results[i];

        std::cout
            << "\n#"
            << i + 1
            << "\n";

        std::cout
            << "Schedule      : "
            << r.schedule_name
            << "\n";

        std::cout
            << "Cycles        : "
            << r.total_cycles
            << "\n";

        std::cout
            << "DRAM Read KB  : "
            << r.dram_read_bytes / 1024.0
            << "\n";

        std::cout
            << "DRAM Write KB : "
            << r.dram_write_bytes / 1024.0
            << "\n";

        std::cout
            << "AI            : "
            << r.arithmetic_intensity
            << "\n";
    }
}

int main(int argc, char** argv)
{
    std::vector<std::string> args;

    for (int i = 1; i < argc; ++i)
        args.emplace_back(argv[i]);

    if (has_arg(args, "--help"))
    {
        print_usage(argv[0]);
        return 0;
    }

    HardwareConfig hw;

    std::cout
        << "==================================================\n"
        << "NPU Tensor Operator Cost Model\n"
        << "==================================================\n";

    hw.print();

    ScheduleSearch search(hw);

    std::string layer =
        get_string(
            args,
            "--layer",
            "conv2d");

    int top_k =
        get_int(
            args,
            "--top",
            10);

    if (layer == "conv2d")
    {
        Conv2DSpec conv;

        conv.batch =
            get_int(args, "--batch", 1);

        conv.in_channels =
            get_int(args, "--in_c", 3);

        conv.in_height =
            get_int(args, "--in_h", 224);

        conv.in_width =
            get_int(args, "--in_w", 224);

        conv.out_channels =
            get_int(args, "--out_c", 64);

        int kernel =
            get_int(args, "--kernel", 3);

        conv.kernel_h = kernel;
        conv.kernel_w = kernel;

        conv.stride =
            get_int(args, "--stride", 1);

        conv.padding =
            get_int(args, "--pad", 1);

        std::cout
            << "\n==================================================\n"
            << "Conv2D Layer\n"
            << "==================================================\n";

        conv.print();

        CostResult best =
            search.find_best_schedule(conv);

        std::cout
            << "\n==================================================\n"
            << "Best Schedule\n"
            << "==================================================\n";

        print_cost_summary(best);

        RooflineAnalyzer::print(
            hw,
            best);

        auto top_results =
            search.rank_conv_candidates(
                conv,
                top_k);

        print_top_results(top_results);
    }
    else if (layer == "matmul")
    {
        MatMulSpec mm;

        mm.M =
            get_int(args, "--M", 512);

        mm.K =
            get_int(args, "--K", 512);

        mm.N =
            get_int(args, "--N", 512);

        std::cout
            << "\n==================================================\n"
            << "MatMul Layer\n"
            << "==================================================\n";

        mm.print();

        CostResult best =
            search.find_best_schedule(mm);

        std::cout
            << "\n==================================================\n"
            << "Best Schedule\n"
            << "==================================================\n";

        print_cost_summary(best);

        RooflineAnalyzer::print(
            hw,
            best);

        auto top_results =
            search.rank_matmul_candidates(
                mm,
                top_k);

        print_top_results(top_results);
    }
    else
    {
        std::cerr
            << "Unknown layer type: "
            << layer
            << "\n";

        print_usage(argv[0]);

        return 1;
    }

    return 0;
}