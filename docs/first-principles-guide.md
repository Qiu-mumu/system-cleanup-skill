# First-Principles System Cleanup Guide

A universal methodology for cleaning Windows systems, grounded in first principles.
Not a checklist — a diagnostic framework.

## The Core Idea

Every computer problem traces back to one or more of these physical resources being exhausted:
- **Disk space** — OS needs >10% free to function
- **Memory (RAM)** — Pagefile of 0 means crash when memory fills
- **CPU cycles** — Background processes steal compute
- **Thermal headroom** — GPU/CPU >60C triggers fans

## Diagnosis Trees

### Fan Noise at Idle
```
CPU frequency >2.2GHz?      -> Power plan issue (set max 99%)
CPU frequency <2.2GHz?
  -> GPU clock >1000MHz?     -> NVIDIA Overlay / external monitor
  -> GPU clock <400MHz?      -> Ambient temp / dust
```

### C Drive Full
```
AppData cache >20GB?         -> pip/npm/Docker/WeChat
Desktop/Downloads >10GB?     -> Move to D: (copy+delete, takes time)
.git/objects >5GB?           -> git gc --aggressive
```

## Safety Rules

| DO NOT Delete | Why |
|--------------|-----|
| WinSxS, assembly, SideBySide | OS component store — breaks Windows |
| Microsoft-signed System32 binaries | Corrupts system |
| pagefile.sys, hiberfil.sys | Causes instability |
| Files locked by SYSTEM processes | Crashes the system |

| Safe to Delete | Note |
|---------------|------|
| pip cache (~9GB) | Regenerates |
| npm cache (~3GB) | Regenerates |
| NVIDIA DXCache (~7GB) | Regenerates on game launch |
| Temp files (~2GB) | Safe |
| Recycle Bin | Safe |

## Reference Commands

```powershell
# Disk space
Get-PSDrive C | Select Free, Used

# GPU temp
nvidia-smi --query-gpu=temperature.gpu,power.draw --format=csv,noheader

# Power plan
powercfg /getactivescheme

# Running services
Get-Service | Where Status -eq Running | Measure

# Service control
sc stop ServiceName
sc config ServiceName start=disabled

# Problem processes
tasklist /fi "IMAGENAME eq MarvisKnowledgebase.exe"
taskkill /f /im MarvisKnowledgebase.exe /t

# Cleanup (safe)
pip cache purge
npm cache clean --force
Clear-RecycleBin -Force
Remove-Item "$env:TEMP\*" -Recurse -Force -ea 0
```

## Priority Levels

P0 — System stability (C: <10% free, pagefile=0)
P1 — Performance (background CPU hogs, GPU locked awake)
P2 — Space recovery (WeChat cache, Desktop clutter)
P3 — Convenience (wallpaper optimization, monitoring setup)

Stop when P0+P1 are resolved and P2 returns <20min.

## Practical Traps

### Cross-Drive Move = Copy + Delete
Moving files from C: to D: with Move-Item is actually a COPY then DELETE.
- 11GB takes ~20-60s on SSD
- Data exists on BOTH drives temporarily — check D: free space first
- For moves >50GB: use obocopy C:\src D:\dst /E /MOVE /R:2 /W:5

### sc config Syntax (Space Trap)
The sc.exe command REQUIRES a space after =:
`atch
REM CORRECT:
sc config ServiceName start= disabled

REM WRONG (fails silently):
sc config ServiceName start=disabled
`
Without the space, sc.exe treats start=disabled as a single unknown token and does nothing.

### Reversibility: Save Original State First
Before any P1+ operation, save the original:
- Service start type: sc qc ServiceName | findstr START_TYPE
- Power plan GUID: powercfg /getactivescheme
- Large directory location: note original path before moving
- System Restore Point: Checkpoint-Computer -Description "Before cleanup"

This gives you a guaranteed undo path.