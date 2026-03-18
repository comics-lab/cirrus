# Hardening Checks

## SSH

Check:
- key-only auth
- root login disabled if appropriate
- effective SSH settings, not just file contents

## Firewall

Check:
- firewall enabled
- default deny inbound
- explicit allowed ports only

## Logging

Check:
- persistent journal
- log rotation
- failed units after boot

## SMART

Check:
- `smartmontools.service` enabled
- expected devices visible
- explicit config if the host has mixed device types

## Power Policy

Check:
- systemd-logind idle behavior
- desktop idle suspend settings for user and greeter
- sleep disabled if unattended stability is required

## Service Surface

Classify enabled services as:
- required
- convenience
- unclear
- remove candidate
