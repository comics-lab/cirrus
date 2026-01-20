Excellent instinct.
Before we touch another disk, container, or database, we name the shape of the lab and the laws it obeys.

What follows is a living architecture document—clear enough to guide decisions, strict enough to prevent entropy, and flexible enough to evolve.

I’ll give you:
	1.	Lab View Architecture (what exists, where, and why)
	2.	Truth Model (what is authoritative vs derived)
	3.	Operational Guidelines (how changes are allowed to happen)
	4.	Decision Guardrails (how we avoid future archaeology)

You can treat this as v1. We can later formalize it into Markdown for GitHub or internal docs.

⸻

📐 Home Lab — Architecture View (v1)

1. Physical & System Topology

Core Systems

The Beast / Reality
	•	Role: Primary workstation + legacy lab authority
	•	Storage:
	•	/mnt/grackle (Btrfs RAID1)
	•	Contains LIBRARY (authoritative comics corpus)
	•	Status:
	•	Actively serving data
	•	Under storage pressure
	•	Operational but architecturally “old generation”

Cirrus
	•	Role: Next-generation lab core
	•	OS:
	•	Debian 13.2
	•	GNOME desktop
	•	Btrfs RAID1 on NVMe (mdraid)
	•	Storage:
	•	NVMe RAID1 → OS, containers, databases
	•	External USB HDD (/dev/sda) → PHOENIX (new intake / rebuild zone)
	•	Status:
	•	Clean install
	•	Not yet hardened
	•	No application state accumulated

⸻

2. Storage Architecture

Storage Roles (Critical Distinction)

Role	Mount	Description
Authoritative	/mnt/grackle/LIBRARY	Canonical, irreplaceable content
Curated Intake	/mnt/phoenix	Controlled rebuild / ingestion zone
Derived / Cache	StoryArcs, staging dirs	Rebuildable, disposable
Operational	NVMe RAID1	OS, Docker, databases

Rule: Authoritative data is never modified by automation.

⸻

/mnt/grackle/LIBRARY — The Crown Jewels
	•	Source of truth for:
	•	Comic files
	•	Naming decisions
	•	Quality decisions
	•	Properties:
	•	Must be readable by all systems
	•	Must not be implicitly “rescanned into submission”
	•	Consequence:
	•	If LIBRARY and Mylar disagree → LIBRARY wins

⸻

/mnt/phoenix — The Rebirth Zone
	•	Lives on external USB HDD (ext4 recommended initially)
	•	Purpose:
	•	Clean ingestion
	•	Logical rebuild
	•	Metadata-first organization
	•	Properties:
	•	Isolated
	•	Reversible
	•	Can be destroyed and recreated without loss
	•	Long-term fate:
	•	Either becomes the new LIBRARY
	•	Or is merged deliberately into grackle

⸻

3. Application Architecture

Container Strategy
	•	Docker only
	•	No secondary orchestrators (CasaOS rejected)
	•	Compose-based definitions
	•	GNOME is not a control plane

Mylar (Next Generation)
	•	Lives on Cirrus
	•	Fresh database
	•	API-driven lifecycle
	•	Metadata sources:
	•	Primary: Metron
	•	Secondary / optional: ComicVine
	•	Responsibilities:
	•	Track series/issues/arcs logically
	•	Never dictate filesystem truth

⸻

4. Truth Model (Non-Negotiable)

Levels of Truth
	1.	Filesystem Truth
	•	Files exist
	•	Bytes are real
	•	LIBRARY is authoritative
	2.	Logical Truth
	•	Series, issues, arcs
	•	Reading order
	•	Derived from metadata sources
	3.	Index Truth
	•	Mylar.db
	•	Search indexes
	•	Disposable

If any two levels disagree, lower number wins.

⸻

Explicit Truth Declarations
	•	Mylar.db may be destroyed at any time
	•	StoryArc directories are views, not data
	•	Reading lists are instructions, not content
	•	Anything labeled “fan-made” is discardable outside LIBRARY

⸻

5. Operational Guidelines

Change Control (Lightweight, Human)

Before any major change:
	1.	Identify affected truth layer
	2.	Confirm authoritative source is untouched
	3.	Ensure rollback path exists

Allowed Automation
	•	Reporting
	•	Comparison
	•	Quarantine
	•	Metadata enrichment

Forbidden Automation
	•	Deleting from LIBRARY
	•	Overwriting LIBRARY files
	•	Silent renames in authoritative paths

⸻

6. Migration Strategy (How Change Happens)

Pattern Used: Parallel Authority
	•	Old system continues to function
	•	New system builds confidence
	•	Cutover only occurs when:
	•	Coverage ≥ old system
	•	Quality ≥ old system
	•	Performance ≥ old system

No big-bang migrations. Ever.

⸻

7. Decision Guardrails (Future-You Insurance)

When faced with a choice, ask:
	1.	Does this increase or reduce the number of “truths”?
	2.	Can I explain this to myself in 6 months?
	3.	If this breaks, do I lose data or convenience?

If the answer is “data” → stop.

⸻

🧭 Where we go next (suggested order)
	1.	Harden Cirrus
	•	users, sudo, firewall, SSH, GNOME hygiene
	2.	Finalize /mnt/phoenix
	•	filesystem, mount, layout
	3.	Document this architecture (Markdown)
	4.	Stand up clean Mylar
	5.	Begin logical ingestion via API

⸻

Final note (important)

What you’re doing now is not cleanup.
It’s establishing constitutional law for your lab.

Everything after this gets easier—not because the work is smaller, but because the rules are clear.

When you’re ready, we can:
	•	turn this into a formal Markdown doc
	•	add diagrams
	•	or write the “Operational Constitution” as a separate, stricter document

Just say the word.
