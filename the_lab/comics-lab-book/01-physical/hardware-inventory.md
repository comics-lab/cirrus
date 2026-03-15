# Hardware Inventory

## Host: Cirrus

## Last Updated
- 2026-01-25 (local time)

## Summary
- Platform: Intel Alder Lake-N (SoC platform)
- GPU: Intel integrated graphics (Alder Lake-N)
- NICs: 2x Intel I226-V
- Wi-Fi: Intel CNVi (AX201)
- NVMe: 2x Kingston NV2 1TB (mdraid RAID1)
- External USB storage: WD My Book Essential (USB)

## PCI Devices (lspci -nn)
```
00:00.0 Host bridge [0600]: Intel Corporation Alder Lake-N Processor Host Bridge/DRAM Registers [8086:461c]
00:02.0 VGA compatible controller [0300]: Intel Corporation Alder Lake-N [Intel Graphics] [8086:46d4]
00:04.0 Signal processing controller [1180]: Intel Corporation Alder Lake Innovation Platform Framework Processor Participant [8086:461d]
00:08.0 System peripheral [0880]: Intel Corporation GNA Scoring Accelerator [8086:467e]
00:0d.0 USB controller [0c03]: Intel Corporation Alder Lake-N Thunderbolt 4 USB Controller [8086:464e]
00:14.0 USB controller [0c03]: Intel Corporation Alder Lake-N PCH USB 3.2 xHCI Host Controller [8086:54ed]
00:14.2 RAM memory [0500]: Intel Corporation Alder Lake-N PCH Shared SRAM [8086:54ef]
00:14.3 Network controller [0280]: Intel Corporation CNVi: Wi-Fi [8086:54f0]
00:15.0 Serial bus controller [0c80]: Intel Corporation Alder Lake-N PCH I2C Controller [8086:54e8]
00:15.1 Serial bus controller [0c80]: Intel Corporation Alder Lake-N PCH I2C Controller [8086:54e9]
00:16.0 Communication controller [0780]: Intel Corporation Alder Lake-N PCH HECI Controller [8086:54e0]
00:1a.0 SD Host controller [0805]: Intel Corporation Alder Lake-N eMMC Controller [8086:54c4]
00:1c.0 PCI bridge [0604]: Intel Corporation Alder Lake-N PCI Express Root Port #1 [8086:54b8]
00:1c.1 PCI bridge [0604]: Intel Corporation Alder Lake-N PCI Express Root Port #2 [8086:54b9]
00:1c.2 PCI bridge [0604]: Intel Corporation Alder Lake-N PCI Express Root Port #3 [8086:54ba]
00:1d.0 PCI bridge [0604]: Intel Corporation Alder Lake-N PCI Express Root Port #9 [8086:54b0]
00:1e.0 Communication controller [0780]: Intel Corporation Alder Lake-N Serial IO UART Host Controller [8086:54a8]
00:1e.3 Serial bus controller [0c80]: Intel Corporation Alder Lake-N Generic SPI (GSPI) Controller [8086:54ab]
00:1f.0 ISA bridge [0601]: Intel Corporation Alder Lake-N PCH eSPI Controller [8086:5481]
00:1f.3 Audio device [0403]: Intel Corporation Alder Lake-N PCH High Definition Audio Controller [8086:54c8]
00:1f.4 SMBus [0c05]: Intel Corporation Alder Lake-N SMBus [8086:54a3]
00:1f.5 Serial bus controller [0c80]: Intel Corporation Alder Lake-N SPI (flash) Controller [8086:54a4]
01:00.0 Ethernet controller [0200]: Intel Corporation Ethernet Controller I226-V [8086:125c] (rev 04)
02:00.0 Ethernet controller [0200]: Intel Corporation Ethernet Controller I226-V [8086:125c] (rev 04)
03:00.0 Non-Volatile memory controller [0108]: Kingston Technology Company, Inc. NV2 NVMe SSD [SM2267XT] (DRAM-less) [2646:5017] (rev 03)
04:00.0 Non-Volatile memory controller [0108]: Kingston Technology Company, Inc. NV2 NVMe SSD [SM2267XT] (DRAM-less) [2646:5017] (rev 03)
```

## USB Devices (lsusb)
```
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 002 Device 003: ID 1058:1140 Western Digital Technologies, Inc. My Book Essential (WDBACW)
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 003: ID 8087:0026 Intel Corp. AX201 Bluetooth
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

## Inventory Tooling
- lspci: available
- lsusb: available
- lshw: not installed
- dmidecode: not installed
