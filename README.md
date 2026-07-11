# First-Principles System Cleanup Skill

A Codex skill for system cleanup built on first principles. Not a "boost your PC" tool — a structured diagnostic framework that traces every deletion to its physical-layer consequences.

## Core Philosophy

1. **Resource Limits**: Disk I/O, RAM, CPU cycles, thermal headroom — all finite. "Junk" is anything consuming these without delivering value.
2. **Action-Consequence Chain**: Every deletion has a downstream effect. Never delete without tracing the consequence.
3. **Reversibility**: Every P1+ operation must have a documented undo path.
4. **Precision over blanket rules**: System caches are safe; OS component stores are not. The skill distinguishes between them.

## Safety Mechanisms

| Mechanism | What it prevents |
|-----------|-----------------|
| File Lock Detection | Deleting files in use by running processes |
| Symlink Detection | Deleting real data on another drive by mistake |
| Service Rebirth Detection | Repeated kill/restart cycles that spike CPU |
| Absolute Fuses | Never-touch list: OS component store, signed binaries, page files |
| Reversibility | Save original state before disabling services or deleting large directories |
| Exit Condition | Stop when marginal benefit < effort cost |

## Edge Cases Covered

From real cleanup sessions:
- Bat file encoding (UTF-16LE causes cmd.exe flash-close)
- `sc config` syntax (the `start= disabled` space requirement)
- NVIDIA Overlay service rebirth (cannot kill, must disable via `sc config`)
- External monitor GPU lock (NVIDIA GPU cannot idle with monitor on HDMI/DP)
- MAX_PATH safe deletion (260-char limit with `del`)
- Cross-drive move = copy + delete (user must be warned about time cost)

## Quick Start

```batch
REM Install the skill to Codex
copy SKILL.md %USERPROFILE%\.codex\skills\system-cleanup\SKILL.md
```

## Trigger Phrases

- "C drive is full"
- "system is slow"
- "fan noise"
- "clean up temp files"
- "disk cleanup"
- "speed up computer"

## Reference Implementation

`CleanUp.bat` — a minimal safe cleanup batch file in ASCII encoding.
Targeted at: pip cache, npm cache, NVIDIA shader cache, Temp files, Recycle Bin.

```batch
@echo off
title CleanUp
pip cache purge
npm cache clean --force
if exist "%USERPROFILE%\.cache\DXCache" (del /f /s /q "%USERPROFILE%\.cache\DXCache\*.*")
del /f /s /q "%TEMP%\*.*"
powershell -Command Clear-RecycleBin -Force
pause
```

## License

MIT
