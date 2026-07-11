# First-Principles System Cleanup

A universal system cleanup framework built on first principles.
Works with: **Codex**, **Claude Code**, **ChatGPT**, **Cursor**, or standalone CLI.

Not a "boost your PC" tool — a structured diagnostic framework that traces every deletion to its physical-layer consequences.

## What's Included

```
system-cleanup-skill/
├── SKILL.md                     # Codex skill (3 modes + 4 safety mechanisms)
│
├── cli/
│   ├── diagnose.py              # Standalone diagnosis tool (read-only, safe)
│   └── config.json              # Junk path database (software -> cache location -> risk)
│
├── docs/
│   └── first-principles-guide.md # Universal guide (any human or AI can follow)
│
├── integrations/
│   └── CLAUDE.md                 # Claude Desktop / Claude Code config
│
├── CleanUp.bat                   # Reference implementation (ASCII safe)
├── examples/
│   └── fan-noise-diagnosis.md    # Real-case walkthrough
├── README.md
├── LICENSE
└── .gitignore
```

## Quick Start

```bash
# Diagnose your system (read-only)
python cli/diagnose.py

# With JSON output (for AI parsing)
python cli/diagnose.py --json
```

## Core Principles

1. **Resource Limits**: Disk, RAM, CPU, thermal headroom — all finite.
2. **Action-Consequence Chain**: Every deletion has a downstream effect.
3. **Reversibility**: Every P1+ operation must have a documented undo path.
4. **Precision**: Distinguish OS binaries (never touch) from system caches (safe).

## Safety Mechanisms

| Mechanism | What it prevents |
|-----------|-----------------|
| File Lock Detection | Deleting files in use by running processes |
| Symlink Detection | Deleting real data on another drive by mistake |
| Service Rebirth Detection | Repeated kill/restart cycles that spike CPU |
| Absolute Fuses | Never-touch list: OS component store, signed binaries, page files |

## Usage with Different AI Tools

| Platform | File | How to use |
|----------|------|-----------|
| Codex | `SKILL.md` | Place in `~/.codex/skills/system-cleanup/SKILL.md` |
| Claude Code / Claude Desktop | `integrations/CLAUDE.md` | Add to project root as `CLAUDE.md` |
| ChatGPT | `docs/first-principles-guide.md` | Copy-paste as Custom Instructions |
| Cursor | `docs/first-principles-guide.md` | Add to `.cursorrules` |

## License

MIT
