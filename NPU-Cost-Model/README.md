NPU Tensor Operator Cost Model
================================

Hi — I'm a kid who got a little carried away building a tiny brain for silicon.
This is my NPU Tensor Operator Cost Model, a small C++ tool I wrote to think
about how convolution and matrix multiplication run on neural accelerators.

Why I made this
---------------

I wanted to understand why some neural network layers scream for memory while
others just want more math. So I built a model that pretends to be a compiler
and estimates cycles, how much data moves around, and whether a layer is
starved for bandwidth or hungry for compute. It's my way of peeking under the
hood of an NPU and making sense of its moods.

What it does (short version)
----------------------------

- Models Conv2D and Matrix Multiply operators and estimates execution latency.
- Simulates a hierarchical memory system: L1 SRAM, L2 SRAM, and DRAM.
- Searches and ranks loop-tiling schedules and common dataflows (Weight-,
  Output-, and Input-Stationary) to find good execution strategies.
- Computes arithmetic intensity and runs a roofline-style analysis to say
  whether a workload is memory-bound or compute-bound.
- Hardware is configurable: change compute array sizes, SRAM capacities,
  bandwidths, and vector units to toy with different chips.

Highlights
----------

- Compiler-inspired schedule search that explores hundreds of candidates.
- Reports cycles, DRAM traffic, SRAM footprints, and arithmetic intensity.
- Small and self-contained C++ command-line tool — no heavy dependencies.

Quick start
-----------

Build (requires a C++ toolchain):

```bash
make
```

Run an example Conv2D search (prints best schedule and top candidates):

```bash
./npu_cost_model --layer conv2d --batch 1 --in_c 3 --in_h 224 --in_w 224 \
  --out_c 64 --kernel 3 --stride 1 --pad 1 --top 5
```

Run an example MatMul search:

```bash
./npu_cost_model --layer matmul --M 512 --K 512 --N 512 --top 5
```

Where to look next
------------------

- [hardware.hpp](hardware.hpp) and related files contain the hardware abstraction.
- [schedule.hpp](schedule.hpp) and [search.hpp](search.hpp) contain the schedule search engine.
- [roofline.hpp](roofline.hpp) contains the roofline analyzer.

If you want changes
-------------------

Tell me what you'd like: different default layer sizes, a friendlier
summary table, or a tiny script that runs a batch of experiments and
saves CSV results. I'm excited to keep building this!

---

Thanks for looking — I hope this little tool helps you tinker with NPU
ideas as much as it helped me. If you spot bugs or weird numbers, please
open an issue or send a patch.
