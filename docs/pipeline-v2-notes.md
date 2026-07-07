# Pipeline V2 Notes

This document captures the next pass at the Cirrus intake pipeline. The goal is to reduce repeated I/O, avoid full-tree rescans, and make each stage reusable from saved artifacts.

## Storage Notes

- `/dev/md0` is the primary local Btrfs-backed NVMe array.
- `/dev/sda` is a single USB3-attached volume.
- Other `/mnt/*` volumes are NFS-mounted partitions.
- Zram may be active.
- The machine has 16 GiB of RAM.
- Swap has historically not been used much, but the workload is I/O-bound before it is memory-bound.

## V2 Operating Model

Use a staged, report-driven pipeline:

1. build or refresh the ComicVine cache from `Projects/CBL-ReadingLists`
2. run prepass normalization once
3. run `cbz_audit` and persist the report
4. run cleanup dry-run and persist the report
5. replay the cleanup report without rescanning
6. rerun `cbz_audit`
7. run Pass 1 / promote only on the surviving, high-confidence set

## Goals

- stop rescanning the same tree at every stage
- keep apply phases report-driven
- minimize full-archive hashing except where needed
- keep writes serialized even when reads are parallel
- preserve provenance by default

## Working Assumptions

- local storage is faster and more reliable than network-mounted paths for the cache and report files
- the main bottleneck is I/O, not swap
- worker counts should scale with the host, but only until the storage layer saturates
- one saved report should be treated as the execution plan for the matching apply phase

