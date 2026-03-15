# Physical Network Layout

## Host: Cirrus

## Last Updated
- 2026-01-25 (local time)

## Interfaces (ip -br link)
```
lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
enp1s0           UP             78:55:36:02:9b:69 <BROADCAST,MULTICAST,UP,LOWER_UP>
enp2s0           DOWN           78:55:36:02:9b:68 <NO-CARRIER,BROADCAST,MULTICAST,UP>
wlo1             UP             98:fe:3e:5e:b6:54 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

## IP Addresses (ip -br addr)
```
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp1s0           UP             192.168.1.113/24 fe80::bc73:5955:c51e:cbc8/64
enp2s0           DOWN
wlo1             UP             192.168.1.79/24 fe80::2f50:5110:8464:b6be/64
```

## Notes
- Two Intel I226-V Ethernet ports detected; one active (enp1s0), one idle (enp2s0).
- Wi-Fi interface wlo1 active.
