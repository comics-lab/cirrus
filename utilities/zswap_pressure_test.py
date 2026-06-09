#!/usr/bin/env python3
"""Allocate anonymous memory to force swap activity for zswap testing."""

from __future__ import annotations

import argparse
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-mib", type=int, default=12000, help="Target MiB to allocate")
    parser.add_argument("--chunk-mib", type=int, default=64, help="Allocation chunk size in MiB")
    parser.add_argument("--hold-seconds", type=int, default=60, help="Seconds to hold allocated memory")
    parser.add_argument("--sleep-seconds", type=float, default=0.05, help="Pause between allocations")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    chunks = []
    chunk_bytes = args.chunk_mib * 1024 * 1024
    total_chunks = args.target_mib // args.chunk_mib

    for _ in range(total_chunks):
        b = bytearray(chunk_bytes)
        for i in range(0, len(b), 4096):
            b[i] = 1
        chunks.append(b)
        time.sleep(args.sleep_seconds)

    print(f"allocated {len(chunks) * args.chunk_mib} MiB; holding for {args.hold_seconds}s")
    time.sleep(args.hold_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
