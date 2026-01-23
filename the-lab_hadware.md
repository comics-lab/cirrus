# Hardware & Physical Documentation Checklist

## General Lab Overview
- [ ] Lab purpose and scope (home lab, comics lab, learning, production)
- [ ] High-level diagram (rack / shelf / desk layout)
- [ ] Power topology (UPS, surge, outlets)
- [ ] Network topology (switches, router, VLANs if any)
- [ ] Environmental notes (cooling, noise, physical access)

---

## Host Inventory (One Section Per Host)

### For EACH host (Cirrus, The Beast, Hippy, Hawkeye, Zima, etc.)
- [ ] Hostname
- [ ] Physical location
- [ ] Role(s) in the lab
- [ ] Manufacturer / model
- [ ] CPU (model, cores)
- [ ] RAM (size, slots used)
- [ ] Internal storage devices
- [ ] External storage devices
- [ ] Network interfaces (speed, MACs if relevant)
- [ ] BIOS/UEFI notes (Secure Boot, TPM, quirks)
- [ ] OS installed (version, install date)
- [ ] Console access method (local, IPMI, none)
- [ ] Known hardware quirks or limitations

---

## Storage Devices (Physical)

### For EACH physical disk or enclosure
- [ ] Device name(s) (historical: sda/sdb/etc)
- [ ] Manufacturer / model
- [ ] Serial number
- [ ] Capacity (decimal and TiB)
- [ ] Interface (SATA, USB, NVMe)
- [ ] Enclosure / adapter used
- [ ] Current filesystem
- [ ] Current role (Boot, Phoenix, Fearless, arcs, pubs, etc.)
- [ ] SMART status notes
- [ ] Purchase date (if known)
- [ ] Replacement / RMA notes (if failed)

---

## Cabling & Physical Connections
- [ ] USB device mapping (which disk on which port)
- [ ] SATA/NVMe slot mapping (if relevant)
- [ ] Network cabling notes
- [ ] UPS connection mapping
- [ ] Labeling scheme (if any)

---

## Failure & Recovery History (Physical)
- [ ] Disk failures (date, symptoms, resolution)
- [ ] Power events (outages, brownouts)
- [ ] Hardware replacements
- [ ] Lessons learned

---

## Photos / Diagrams (Optional but Valuable)
- [ ] Host photos (inside/outside)
- [ ] Disk labels photographed
- [ ] Cabling layout photo
- [ ] Rack/shelf overview photo
