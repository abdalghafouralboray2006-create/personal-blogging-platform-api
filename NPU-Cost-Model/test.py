import subprocess
import itertools
import sys

BINARY = "./npu_cost_model"


def run(cmd):
    """Run C++ binary and capture output."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return result.stdout


def test_conv2d():
    print("\n==============================")
    print("Testing Conv2D Scaling")
    print("==============================")

    configs = [
        (1, 3, 224, 224, 64),
        (1, 32, 112, 112, 128),
        (1, 64, 56, 56, 256),
    ]

    for c in configs:
        cmd = [
            BINARY,
            "--layer", "conv2d",
            "--batch", str(c[0]),
            "--in_c", str(c[1]),
            "--in_h", str(c[2]),
            "--in_w", str(c[3]),
            "--out_c", str(c[4]),
        ]

        output = run(cmd)

        print("\nConfig:", c)
        print(output.split("\n")[-20:])  # last part only


def test_matmul():
    print("\n==============================")
    print("Testing MatMul Scaling")
    print("==============================")

    configs = [
        (128, 128, 128),
        (256, 256, 256),
        (512, 512, 512),
    ]

    for c in configs:
        cmd = [
            BINARY,
            "--layer", "matmul",
            "--M", str(c[0]),
            "--K", str(c[1]),
            "--N", str(c[2]),
        ]

        output = run(cmd)

        print("\nConfig:", c)
        print(output.split("\n")[-20:])


def stress_tile_sensitivity():
    print("\n==============================")
    print("Testing Tile Sensitivity")
    print("==============================")

    # same workload, different behavior expected
    configs = [
        (16, 16, 16),
        (32, 32, 32),
        (64, 64, 64),
        (128, 128, 128),
    ]

    for c in configs:
        cmd = [
            BINARY,
            "--layer", "matmul",
            "--M", str(c[0]),
            "--K", str(c[1]),
            "--N", str(c[2]),
        ]

        output = run(cmd)

        print("\nTile pressure test:", c)
        print(output.split("\n")[-15:])


def sanity_check_growth():
    print("\n==============================")
    print("Sanity Check: Monotonic Growth")
    print("==============================")

    prev_cycles = None

    for size in range(64, 513, 64):
        cmd = [
            BINARY,
            "--layer", "matmul",
            "--M", str(size),
            "--K", str(size),
            "--N", str(size),
        ]

        output = run(cmd)

        # crude extraction: look for "Total Cycles"
        cycles = None
        for line in output.split("\n"):
            if "Total Cycles" in line:
                try:
                    cycles = int(line.split(":")[-1].strip())
                except:
                    pass

        print(f"Size {size}: {cycles}")

        if prev_cycles is not None:
            if cycles < prev_cycles:
                print("WARNING: non-monotonic behavior detected")

        prev_cycles = cycles


def main():
    print("NPU Cost Model Test Suite")

    test_conv2d()
    test_matmul()
    stress_tile_sensitivity()
    sanity_check_growth()


if __name__ == "__main__":
    main()