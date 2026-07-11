# System Cleanup Skill — CLAUDE.md

## Core Principles

1. **Resource Limits**: Disk, RAM, CPU, thermal headroom are finite.
2. **Action-Consequence Chain**: Every deletion has a downstream effect.
3. **Reversibility**: P1+ operations need an undo path.
4. **Precision**: Distinguish OS binaries (never touch) from system caches (safe).

## Safety Rules (Never Violate)

- NEVER delete OS component store: WinSxS, assembly, SideBySide
- NEVER delete Microsoft-signed binaries under C:\Windows\System32\
- NEVER delete pagefile.sys, hiberfil.sys, swapfile.sys
- NEVER delete files locked by SYSTEM or critical processes
- NEVER follow symlinks blindly — show the real physical target path

## When User Reports "C drive is full"
1. Run: Get-PSDrive C (check free space)
2. If <10% free, check: pip cache, npm cache, NVIDIA DXCache, Temp, WeChat
3. Check .git/objects — can reach 10-50GB on dev machines
4. Move desktop/Downloads to D: (warn: cross-drive = copy+delete)
5. Never delete without showing the consequence table

## When User Reports "Fan is loud at idle"
1. Check power plan — if on Performance, switch to throttled plan
2. Check GPU clock (nvidia-smi) — >1000MHz at idle is abnormal
3. Check NVIDIA Overlay — 5 instances block GPU from sleeping
4. Check Marvis/QQ Music background processes
5. External monitor on HDMI/DP — GPU cannot fully idle
6. Ambient temperature — if >35C, fan noise is expected

## Process Kill Order
1. Stop service (net stop)
2. Disable service (sc config start=disabled)
3. Kill child processes (taskkill)
Wrong order causes service rebirth (thrashing).

## Bat File Encoding Rule
All .bat files must be ASCII or UTF-8 without BOM.
UTF-16LE files cause cmd.exe flash-close.
Use: [System.IO.File]::WriteAllText(path, content, [Text.Encoding]::ASCII)
