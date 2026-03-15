# Physical Storage Inventory

## Host: Cirrus

## Last Updated
- 2026-01-25 (local time)

## Block Devices (lsblk)
```
NAME           SIZE MODEL                SERIAL           TRAN   ROTA FSTYPE            MOUNTPOINTS  UUID
sda            3.6T HGST HDS5C4040ALE630 PL1331LAGG248H   usb       1
└─sda1         3.6T                                                 1 btrfs             /mnt/phoenix 02d9bc81-c5b0-4ba9-beab-50cf314b3eb2
mmcblk0       58.2G                      0xcd30b932       mmc       0
├─mmcblk0p1    100M                                       mmc       0 vfat                           8847-30F9
├─mmcblk0p2     16M                                       mmc       0
├─mmcblk0p3      1G                                       mmc       0 ntfs                           AC6891296890F376
└─mmcblk0p4   57.1G                                       mmc       0 ntfs                           E83094083093DC3E
nvme0n1      931.5G KINGSTON SNV2S1000G  50026B76860DF86F nvme      0
└─nvme0n1p1  931.5G                                       nvme      0 linux_raid_member              4f2696d5-4204-6ba0-5aff-7f98dc86875c
  └─md0      930.9G                                                 0
    └─md0p1  930.9G                                                 0 btrfs             /home        8f8bd0c2-452d-4095-b4e9-2cd4c9027f52
                                                                                        /
nvme1n1      931.5G KINGSTON SNV2S1000G  50026B76860DFFB3 nvme      0
├─nvme1n1p1    487M                                       nvme      0 vfat              /boot/efi    8EBB-3633
└─nvme1n1p2    931G                                       nvme      0 linux_raid_member              4f2696d5-4204-6ba0-5aff-7f98dc86875c
  └─md0      930.9G                                                 0
    └─md0p1  930.9G                                                 0 btrfs             /home        8f8bd0c2-452d-4095-b4e9-2cd4c9027f52
                                                                                        /
```

## Roles
- Boot volume: Btrfs on md0p1 (NVMe RAID1), subvols / and /home
- Phoenix: /dev/sda1 (Btrfs, USB HDD) mounted at /mnt/phoenix

## Notes
- Phoenix currently contains a recovered filesystem and will be wiped and re-initialized for Cirrus use.
- Phoenix is currently 83-84% full (see state-of-hardware-20260126-055629.txt).
