# Service Classification

## Required

Typical examples:
- SSH or other remote access the host depends on
- networking and Wi-Fi support
- storage monitoring or RAID support
- firewall or update services that are part of the hardening baseline

## Intentional Convenience

Typical examples:
- minimal desktop display manager
- Bluetooth kept for a real device workflow
- Avahi kept for stable `.local` discovery on a LAN

## Unclear

Use this bucket when:
- the service is active but not documented
- the host might need it, but the reason is not yet verified
- removing it now would risk breaking hardware support or login behavior

## Remove Candidate

Use this bucket when:
- the service does not support the documented host role
- the service adds attack surface or boot complexity
- the service can be removed in a small, validated change wave

## Review Questions

Ask for each service:
- what host role does this support?
- is that role intentional?
- does the host still work without it?
- should it be kept now, reviewed later, or removed?
