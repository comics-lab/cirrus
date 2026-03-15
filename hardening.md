Perfect. This is the right division of labor: you harden Cirrus, I write the book.

I’ll give you (A) a practical Debian hardening checklist you can work through immediately, then (B) a concrete documentation set—file names, purposes, and cross-links—so what I draft drops cleanly into a GitHub org as a wiki or repo.

No fluff. This is ops-grade.

⸻

A) Debian 13 Server Hardening — Checklist (Cirrus)

## Observed State (2026-01-26)
- SSH: PermitRootLogin no, PasswordAuthentication no, PubkeyAuthentication yes
- UFW: active, default deny incoming, SSH allowed
- Services: ssh enabled; ufw enabled; unattended-upgrades enabled; nftables disabled; fail2ban not installed
- Journald: Storage=persistent configured
- Log rotation: logrotate.timer enabled
- State log: state-of-hardware-20260126-055629.txt

## Observed State (2026-03-15)
- SMART tooling: `smartmontools` installed
- SMART service: `smartmontools.service` enabled and running
- SMART config: explicit entries for `/dev/sda -d sat`, `/dev/nvme0 -d nvme`, and `/dev/nvme1 -d nvme`
- SMART alert path: `smartd-runner`
- Phoenix SMART: available through the USB bridge and readable with `smartctl -d sat /dev/sda`

Treat this as a check sheet, not a tutorial. Each item is intentional.

⸻

1. Base System Hygiene
	•	Fully update system

sudo apt update && sudo apt full-upgrade
sudo apt autoremove --purge


	•	Set correct hostname + FQDN

hostnamectl set-hostname cirrus


	•	Set timezone & locale

timedatectl set-timezone <yours>
locale-gen



⸻

2. Users, Auth, and Sudo
	•	Confirm only one human user (uid 1000) has sudo

getent group sudo


	•	Disable root login password

sudo passwd -l root


	•	Enforce strong sudo policy

sudo visudo

Recommended:

Defaults use_pty
Defaults logfile="/var/log/sudo.log"



⸻

3. SSH Hardening (Critical)
	•	Install OpenSSH server (if not already)
	•	Switch to key-only auth

PasswordAuthentication no
PubkeyAuthentication yes


	•	Disable root login

PermitRootLogin no


	•	Reduce attack surface

AllowUsers rmleonard
MaxAuthTries 3
LoginGraceTime 30


	•	Restart and test from another terminal

sudo systemctl restart ssh



⸻

4. Firewall (ufw)
	•	Enable ufw

sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing


	•	Allow only what you need (example)

sudo ufw allow ssh
sudo ufw enable
sudo ufw status verbose



⸻

5. Kernel & Sysctl Baseline
	•	Harden network stack
/etc/sysctl.d/99-hardening.conf

net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
net.ipv4.tcp_syncookies=1
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.default.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.default.send_redirects=0


	•	Apply

sudo sysctl --system



⸻

6. Services & Attack Surface Reduction
	•	List enabled services

systemctl list-unit-files --state=enabled


	•	Disable anything not explicitly required
	•	Remove unused packages (avahi, cups, etc. if not needed)

⸻

7. Filesystem & Permissions
	•	Verify no world-writable directories (outside /tmp)

sudo find / -xdev -type d -perm -0002


	•	Mount options sanity:
	•	noexec,nosuid,nodev where appropriate
	•	Confirm /mnt/phoenix not auto-mounted by desktop

⸻

8. Logging & Auditing (Lightweight)
	•	Ensure journald persistent

Storage=persistent


	•	Log rotation working
	•	Optional: fail2ban (only if SSH exposed)

⸻

9. Snapshots / Rollback (Optional but recommended)
	•	Take a Btrfs snapshot after hardening
	•	Label it: post-hardening

⸻

Stop Point

When all boxes are checked:

Cirrus is now a hardened server that happens to have GNOME.

Do not install Docker until this is done.

⸻

B) “The Book” — Documentation Architecture

This is the structure I recommend.
It works as:
	•	a GitHub repo or
	•	a GitHub Wiki or
	•	both (repo + wiki mirror)

I’ll draft these in clean Markdown.

⸻

Repository Name (suggested)

cirrus-lab-book

or under your org:

comics-lab-book


⸻

Top-Level Structure

/
├── README.md                # What this lab is, how to read the book
├── architecture/
│   ├── overview.md          # High-level system view
│   ├── storage.md           # grackle / phoenix / truth model
│   ├── network.md           # hosts, ports, firewall philosophy
│   └── diagrams/            # Mermaid diagrams
├── truth/
│   ├── truth-model.md       # Authoritative vs derived rules
│   ├── deletion-policy.md  # What may be deleted and when
│   ├── naming-policy.md    # File naming and normalization rules
│   └── fanmade-policy.md   # Explicit discard rules
├── systems/
│   ├── cirrus.md            # Build, hardening, role
│   ├── beast.md             # Legacy system notes
│   └── phoenix.md           # Intake & rebuild zone
├── containers/
│   ├── docker-baseline.md   # Why Docker, how configured
│   ├── mylar/
│   │   ├── overview.md
│   │   ├── api-usage.md
│   │   ├── ingestion-flow.md
│   │   └── migration-notes.md
│   ├── kavita/
│   │   ├── overview.md
│   │   ├── library-mapping.md
│   │   └── metadata.md
│   └── portainer.md
├── automation/
│   ├── scripts.md           # What scripts exist and why
│   ├── comparison-tools.md # Dedup, quality scoring, etc.
│   └── scheduled-jobs.md
├── agents.md                # Human + system roles (see below)
└── CHANGELOG.md             # Decisions, not commits


⸻

agents.md — What this document is for

This is important and underused.

agents.md defines who/what is allowed to act and within what bounds.

Example sections:

# Agents

## Human Agents
- rmleonard
  - Full authority
  - Final arbiter of truth conflicts

## System Agents
- Mylar
  - Index-only authority
  - May not rename or delete files in LIBRARY
- Kavita
  - Read-only access to libraries
- Automation Scripts
  - Report, compare, quarantine only

## Forbidden Actions
- Automated deletion in LIBRARY
- Automated renames without dry-run

This prevents future-you from accidentally letting a tool “decide”.

⸻

“Truth Documents” (why they matter)

These are the constitution of the lab.

They answer:
	•	What is real?
	•	What can be rebuilt?
	•	What must never be touched automatically?

I will draft:
	•	truth-model.md
	•	deletion-policy.md
	•	fanmade-policy.md

using the rules we’ve already established.

⸻

What I’ll do next (while you harden Cirrus)

I will:
	1.	Draft Architecture Overview (architecture/overview.md)
	2.	Draft Storage & Truth Model
	3.	Draft agents.md
	4.	Draft Mylar + Kavita usage docs (v1)

When you’re done hardening, we converge:
	•	install Docker
	•	create /mnt/phoenix
	•	then align the docs with reality (no doc rot)

⸻

How to resume cleanly

When you come back after hardening, say:

“Cirrus hardened — checklist complete.”

I’ll then:
	•	ask only the deltas that matter,
	•	proceed to Docker baseline,
	•	and drop the first batch of Markdown files ready for GitHub.

You’re not just building a lab.

You’re writing the manual you wish every past system had come with.

Go harden Cirrus. I’ve got the pen.
