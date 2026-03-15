Yep — Cirrus is a whole campaign, not a single battle. The good news: we can make it boring, repeatable, and “future-you-proof” with a tight, staged checklist.

Below is a practical Cirrus bring-up plan in the order I’d run it, with concrete commands and deliverables. Treat it like a flight checklist: don’t skip ahead.

⸻

## Status Snapshot (2026-01-26)
- State log: state-of-hardware-20260126-055629.txt
- OS: Debian GNU/Linux 13 (trixie), kernel 6.12.63+deb13-amd64
- Boot volume: Btrfs on md0p1 (NVMe RAID), subvols / and /home
- Phoenix: /mnt/phoenix on /dev/sda1 (Btrfs), fstab entry present, mounted; 3.7T total, 84% used
- SSH hardening: PermitRootLogin no, PasswordAuthentication no, PubkeyAuthentication yes
- Firewall: UFW active, default deny incoming, SSH allowed
- Services: ssh enabled; ufw enabled; unattended-upgrades enabled; nftables disabled; fail2ban not installed
- Journald: Storage=persistent configured
- Log rotation: logrotate.timer enabled

Phase 1: Freeze the ground truth

Capture baseline “truth bundle”

Run these and save outputs into ~/Projects/cirrus/truth/ (or your ops repo):

mkdir -p ~/Projects/cirrus/truth
{
  date
  uname -a
  lsb_release -a 2>/dev/null || cat /etc/os-release
  uptime
  ip a
  ip r
  lsblk -o NAME,SIZE,MODEL,SERIAL,TRAN,FSTYPE,MOUNTPOINTS
  findmnt -o SOURCE,FSTYPE,TARGET,OPTIONS
  df -hT
  sudo btrfs filesystem show
  sudo btrfs filesystem df /
  sudo btrfs device stats /
} | tee ~/Projects/cirrus/truth/baseline.txt

Deliverable: baseline.txt committed to your Cirrus ops/docs repo.

⸻

Phase 2: Security hardening (host)

A. Accounts + SSH
	•	Ensure key-only SSH, no password auth, no root login.

Check:

sudo sshd -T | egrep 'passwordauthentication|permitrootlogin|pubkeyauthentication'

Recommended settings in /etc/ssh/sshd_config.d/ (not inline edits):
	•	PasswordAuthentication no
	•	PermitRootLogin no
	•	PubkeyAuthentication yes

Reload:

sudo systemctl reload ssh

B. Firewall (nftables or ufw)

Pick one. I lean nftables on Debian, but ufw is fine if you’ll actually maintain it.

Minimum inbound: SSH only (and later, only what you explicitly need for reverse proxy / monitoring).

C. Auto security updates

sudo apt update
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades

D. Basic host hygiene

sudo apt install -y fail2ban logrotate auditd

Deliverable: hardening.md updated with what you applied and why.

⸻

Phase 3: Storage layout (Boot Volume + Phoenix)

You already set the mental model: Boot Volume + Phoenix.

What we need next is to ensure:
	•	Phoenix exists (formatted, mounted, fstab’d)
	•	Docker data and all container volumes live on Phoenix
	•	Permissions and ownership are deliberate

Deliverable: logical_storage.md finalized + /etc/fstab documented.

⸻

Phase 4: Docker “safety-first” setup

A. Install Docker the Debian way (or Docker repo—your call)

I recommend Docker’s repo for freshness; Debian packages for stability. Either is fine if documented.

B. Configure Docker daemon safely

Create /etc/docker/daemon.json like:
	•	log rotation
	•	no experimental features
	•	sane defaults

Example starting point:

{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5" }
}

Reload:

sudo systemctl restart docker

C. Put Docker data on Phoenix (important)

Either:
	•	bind-mount Phoenix into /var/lib/docker, or
	•	set Docker data-root to Phoenix

Data-root approach:

{ "data-root": "/mnt/phoenix/docker", "log-driver": "json-file", "log-opts": {"max-size":"10m","max-file":"5"} }

Deliverable: software_services.md updated + docker config committed.

⸻

Phase 5: Container platform + guardrails

Decide the control plane:
	•	docker compose (simple, recommended)
	•	Portainer (optional; you already run it elsewhere)

My suggestion for Cirrus:
	•	Use compose as canonical (Git)
	•	Portainer, if you want, should read stacks from Git—not be the source of truth

Deliverable: compose/ directory with:
	•	one docker-compose.yml per service group
	•	.env templates (no secrets committed)

⸻

Phase 6: Apps (in the right order)

Recommended deployment order:
	1.	Reverse proxy (if you’ll expose web UIs)
	•	Caddy or Traefik
	2.	Core data services (if needed)
	•	postgres/redis (only if a stack requires it)
	3.	Kavita
	4.	Mylar
	5.	jDownloader (maybe moved to Hippy as you suggested)
	6.	Monitoring (node_exporter, cAdvisor, etc.)

Each service gets:
	•	a compose file
	•	a persistent volume path on Phoenix
	•	a runbook section (start/stop/backup/restore)

⸻

Phase 7: Backups + “oh no” plan (before you get comfy)

Even if you don’t implement full backups today, you need:
	•	what is backed up
	•	where it goes
	•	how to restore
	•	how often

Deliverable: runbooks/restore.md + backup.md.

⸻

What I need from you next (minimal)

When you’re ready to resume Cirrus work, paste:
	1.	lsblk -f from Cirrus
	2.	findmnt from Cirrus
	3.	cat /etc/fstab from Cirrus (redact anything sensitive)

And I’ll turn that into:
	•	the exact Phoenix mount + permissions plan
	•	the Docker data-root move plan
	•	a first compose skeleton for Kavita + Mylar (safe defaults)

We’ll make Cirrus boring enough that it’s practically a household appliance.
