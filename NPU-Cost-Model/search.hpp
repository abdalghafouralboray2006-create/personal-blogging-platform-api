#pragma once

#include <vector>
#include <limits>
#include <algorithm>

#include "hardware.hpp"
#include "layer.hpp"
#include "schedule.hpp"
#include "cost_model.hpp"

class ScheduleSearch {
public:
    explicit ScheduleSearch(const HardwareConfig& hw)
        : hw_(hw), cost_model_(hw) {}

    CostResult find_best_schedule(const Conv2DSpec& layer) const {
        CostResult best;
        best.total_cycles = std::numeric_limits<long long>::max();

        for (int toc : conv_channel_tiles_) {
            if (toc > layer.out_channels) continue;

            for (int tic : conv_channel_tiles_) {
                if (tic > layer.in_channels) continue;

                for (int toh : conv_spatial_tiles_) {
                    if (toh > layer.output_height()) continue;

                    for (int tow : conv_spatial_tiles_) {
                        if (tow > layer.output_width()) continue;

                        for (auto dataflow : conv_dataflows()) {

                            Conv2DSchedule sched;

                            sched.toc = toc;
                            sched.tic = tic;
                            sched.toh = toh;
                            sched.tow = tow;
                            sched.dataflow = dataflow;

                            auto result =
                                cost_model_.evaluate(layer, sched);

                            if (!result.fits_l2)
                                continue;

                            if (result.total_cycles <
                                best.total_cycles)
                            {
                                best = result;
                            }
                        }
                    }
                }
            }
        }

        return best;
    }

    CostResult find_best_schedule(const MatMulSpec& layer) const {
        CostResult best;
        best.total_cycles = std::numeric_limits<long long>::max();

        for (int tm : matmul_tiles_) {
            if (tm > layer.M) continue;

            for (int tn : matmul_tiles_) {
                if (tn > layer.N) continue;

                for (int tk : matmul_tiles_) {
                    if (tk > layer.K) continue;

                    for (auto dataflow : matmul_dataflows()) {

                        MatMulSchedule sched;

                        sched.tm = tm;
                        sched.tn = tn;
                        sched.tk = tk;
                        sched.dataflow = dataflow;

                        auto result =
                            cost_model_.evaluate(layer, sched);

                        if (!result.fits_l2)
                            continue;

                        if (result.total_cycles <
                            best.total_cycles)
                        {
                            best = result;
                        }
                    }
                }
            }
        }

        return best;
    }

    std::vector<CostResult>
    rank_conv_candidates(
        const Conv2DSpec& layer,
        std::size_t top_k = 10) const
    {
        std::vector<CostResult> results;

        for (int toc : conv_channel_tiles_) {
            if (toc > layer.out_channels) continue;

            for (int tic : conv_channel_tiles_) {
                if (tic > layer.in_channels) continue;

                for (int toh : conv_spatial_tiles_) {
                    if (toh > layer.output_height()) continue;

                    for (int tow : conv_spatial_tiles_) {
                        if (tow > layer.output_width()) continue;

                        for (auto df : conv_dataflows()) {

                            Conv2DSchedule sched;

                            sched.toc = toc;
                            sched.tic = tic;
                            sched.toh = toh;
                            sched.tow = tow;
                            sched.dataflow = df;

                            auto r =
                                cost_model_.evaluate(layer, sched);

                            if (r.fits_l2)
                                results.push_back(r);
                        }
                    }
                }
            }
        }

        sort_results(results);

        if (results.size() > top_k)
            results.resize(top_k);

        return results;
    }

    std::vector<CostResult>
    rank_matmul_candidates(
        const MatMulSpec& layer,
        std::size_t top_k = 10) const
    {
        std::vector<CostResult> results;

        for (int tm : matmul_tiles_) {
            if (tm > layer.M) continue;

            for (int tn : matmul_tiles_) {
                if (tn > layer.N) continue;

                for (int tk : matmul_tiles_) {
                    if (tk > layer.K) continue;

                    for (auto df : matmul_dataflows()) {

                        MatMulSchedule sched;

                        sched.tm = tm;
                        sched.tn = tn;
                        sched.tk = tk;
                        sched.dataflow = df;

                        auto r =
                            cost_model_.evaluate(layer, sched);

                        if (r.fits_l2)
                            results.push_back(r);
                    }
                }
            }
        }

        sort_results(results);

        if (results.size() > top_k)
            results.resize(top_k);

        return results;
    }

private:
    HardwareConfig hw_;
    CostModel cost_model_;

    const std::vector<int> conv_channel_tiles_ {
        8, 16, 32, 64, 128
    };

    const std::vector<int> conv_spatial_tiles_ {
        8, 16, 32, 64
    };

    const std::vector<int> matmul_tiles_ {
        16, 32, 64, 128, 256, 512
    };

    std::vector<Dataflow> conv_dataflows() const {
        return {
            Dataflow::WeightStationary,
            Dataflow::OutputStationary,
            Dataflow::InputStationary
        };
    }

    std::vector<Dataflow> matmul_dataflows() const {
        return {
            Dataflow::WeightStationary,
            Dataflow::OutputStationary,
            Dataflow::InputStationary
        };
    }

    static void sort_results(
        std::vector<CostResult>& results)
    {
        std::sort(
            results.begin(),
            results.end(),
            [](const CostResult& a,
               const CostResult& b)
            {
                return a.total_cycles <
                       b.total_cycles;
            });
    }
};