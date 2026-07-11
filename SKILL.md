# First-Principles System Cleanup Skill

## Trigger
Use when the user reports: C drive is full, system is slow, fan noise, wants to clean temporary files, clear cache, uninstall bloatware, or optimize startup items. Also triggers when the user mentions "disk cleanup", "system optimization", or "speed up computer".

## Core Principles (First Principles)

1. **Resource Limits**: A computer's fundamental resources (disk I/O, RAM, CPU cycles, thermal headroom) are finite. "Junk" is anything consuming these resources without providing value.
2. **Action-Consequence Chain**: Every deletion has a downstream effect. Never delete without tracing the consequence.
3. **Data Ownership**: The user owns their data. Never execute destructive operations without explicit, informed consent.
4. **Minimal Intervention**: Only act on what the user has pain points with. Don't scan/purge for its own sake.

## Safety Hardening (Critical)

### Edge Case 1: File Lock / Dynamic Occupation
- Before deleting any file, check if it belongs to a running process.
- Use lsof (macOS/Linux) or handle.exe / PowerShell Get-Process + file check (Windows).
- If locked, NEVER force-terminate the holding process without warning about unsaved data.
- Risk level: HIGH - terminating the wrong process can crash the application or lose data.

### Edge Case 2: Symbolic Links / Junctions / Reparse Points
- Modern software (Docker, WeChat, OneDrive, Steam) redirects data via symlinks to other drives.
- A naive scanner that follows paths will mistake a symlink for the real data location.
- Deleting a symlink target = deleting the REAL files on the other drive.
- Safety rule: **If path contains reparse point / symlink, flag it and show the real physical target path.** Never treat it as a regular directory.

### Edge Case 3: Service Rebirth (The Thrashing Effect)
- System-level services (NVIDIA Container, Marvis, antivirus, etc.) auto-restart when killed.
- Repeated kill/restart cycles spike CPU and make the system **slower**, not faster.
- Safety rule: Distinguish between **application-level processes** (safe to kill) and **daemon/service-level processes** (must disable via service manager, not kill).
- For services: use sc config <name> start= disabled (Windows) or systemctl disable (Linux), not 	askkill.

### Edge Case 4: Pagefile / Hibernation Files
- pagefile.sys and hiberfil.sys are large files on C: that users often want to delete.
- Deleting pagefile.sys (virtual memory) causes instability under memory pressure.
- Deleting hiberfil.sys disables fast startup and sleep.
- Rule: Never delete these files. Offer to **resize** or **move** them instead.

## Workflow & Modes

### Mode 0: Pain Point Diagnosis
Before scanning, ask:
1. What specific problem are you experiencing? (C: full? Slow boot? Fan noise? App crash?)
2. What have you tried already?
3. Which drive is the issue on? (C:, D:, etc.)

Then propose one of the following directions:

| Direction | Scope | Risk |
|-----------|-------|------|
| A: System Slimming | Temp files, logs, prefetch, update cache | Low |
| B: App Deep Clean | Browser cache, chat app cache, IDE caches | Medium (may need re-login) |
| C: Memory & Startup | Disable startup items, stop unnecessary services | Medium (service rebirth risk) |
| D: Uninstall Residue | AppData orphan data, dead registry entries | High (can break other apps) |

### Mode 1: Scan & Assessment
Run targeted scans based on the chosen direction. Output a structured table:

| Category | Target Path | Size | Status (Idle/Locked) | If Deleted | If Kept |
|----------|------------|------|---------------------|------------|---------|
| Example | %TEMP%\*.tmp | 2.3GB | Locked (explorer.exe) | App crash risk | Slow growth continues |

**Rules:**
- Only scan paths relevant to the chosen direction. No full-disk scans.
- Check each file's lock status before reporting.
- If symlink detected, add a column Real Path: D:\real\data.
- After showing the table, **stop and wait** for user selection.

### Mode 2: Safety-Fused Execution

**Absolute Fuses (never touch):**
- **OS component store**: C:\Windows\WinSxS\, C:\Windows\assembly\, C:\Windows\SideBySide\
- **Signed system binaries**: Any .exe/.dll under C:\Windows\System32\ that is Microsoft-signed (check with Get-AuthenticodeSignature)
- **Page files**: pagefile.sys, hiberfil.sys, swapfile.sys
- **Service registry keys**: HKLM\SYSTEM\CurrentControlSet\Services\
- **Critical process locked files**: csrss.exe, smss.exe, wininit.exe, services.exe
- **Symlinks to protected paths**
- **Exceptions** (safe system caches): C:\Windows\Temp\*, C:\Windows\LogFiles\, C:\Windows\SoftwareDistribution\Download\*

**Secondary Confirmation Required for:**
- AppData folder (profile data, may contain credentials/sessions)
- Browser cache (will sign out of websites)
- Chat app cache (WeChat/QQ - will lose chat history)
- Any file > 1GB that is not a clearly safe cache

**Safe Execution Pattern (Windows):**
`powershell
# Safe: pip/npm cache (recreates on demand)
pip cache purge
npm cache clean --force

# Safe: NVIDIA shader cache (recreates when game launches)
Remove-Item "%USERPROFILE%\.cache\DXCache\*" -Recurse -Force

# Safe: User temp files
Remove-Item "%TEMP%\*" -Recurse -Force -ErrorAction SilentlyContinue

# Safe: Recycle Bin
Clear-RecycleBin -Force

# Semi-safe: Windows Update cache (needs admin, service restart)
# net stop wuauserv; del /f /s /q "%windir%\SoftwareDistribution\Download\*.*"; net start wuauserv

# Service disable (not kill - prevents rebirth):
# sc.exe stop ServiceName
# sc.exe config ServiceName start= disabled
`

## Reference Implementation: CleanUp.bat

A minimal, safe cleanup batch file (ASCII encoding, zero Chinese, no encoding issues):

`atch
@echo off
title CleanUp
echo Step 1: pip cache
pip cache purge
echo Step 2: npm cache
npm cache clean --force
echo Step 3: NVIDIA shader cache
if exist \"%USERPROFILE%\.cache\DXCache\" (
    del /f /s /q \"%USERPROFILE%\.cache\DXCache\*.*\"
)
echo Step 4: Temp files
del /f /s /q \"%TEMP%\*.*\"
echo Step 5: Recycle Bin
powershell -Command Clear-RecycleBin -Force
pause
`

**Encoding Rule**: Bat files MUST be ASCII or UTF-8 without BOM. Chinese characters cause cmd.exe flash-close. Use English-only output, or write in PowerShell (.ps1).

## Reference Sources

- **BleachBit** (github.com/bleachbit/bleachbit): Open-source cleaner. Read cleaners/*.xml for per-software junk path databases and risk levels.
- **Windows Internals (7th Ed.)** - Mark Russinovich: Chapters on Memory Management and Page Files for authoritative pagefile/hibernation consequence analysis.
- **CSAPP (Computer Systems: A Programmer's Perspective)** - Bryant & O'Hallaron: Chapter on cache locality for explaining why cache deletion causes temporary slowdown.
- **Microsoft Docs - Service Control (sc.exe)**: Official documentation for service lifecycle management.

## Reversibility Principle
Any P1+ operation MUST have an undo path documented before execution.

1. **Before disabling a service**: Save the original START_TYPE
   `sc qc ServiceName | findstr START_TYPE` -> note value, THEN disable
   Undo: `sc config ServiceName start= <original_value>`

2. **Before deleting large directory (>1GB)**: Move to quarantine first
   Verify stability for 1 boot cycle, THEN delete quarantine.

3. **Before modifying power plan**: Save original GUID for undo.

4. **System Restore Point** (admin rights): Checkpoint-Computer

## Exit Condition (Bounded Effort)
Stop when further optimization benefit < effort cost:
- C: drive >20% free -> stop scanning large caches
- GPU idle temp <50C -> stop investigating fan noise
- Boot time <30s -> stop optimizing startup

## Decision Trees for Multi-Cause Problems

### Fan Noise at Idle
Check CPU frequency -> if >2.2GHz -> power plan / background processes
                      -> if <2.2GHz -> check GPU
                           -> GPU >1000MHz -> NVIDIA Overlay / external monitor
                           -> GPU <400MHz -> ambient temp / dust

### C Drive Low on Space
AppData cache >20GB -> pip/npm/Docker/WeChat/Android SDK
Desktop/Downloads >10GB -> move to D: (cross-drive = copy+delete, warn user)
.git/objects >5GB -> git gc --aggressive

## Output Constraints

- Zero emotional language. No "your computer will fly" or "boost performance".
- For every deletion, state: (1) what is being deleted, (2) why it exists, (3) what happens immediately after deletion, (4) what happens long-term.
- If user asks for an action that violates safety rules, explain why and offer a safer alternative.
- Keep responses concise. Use tables for data, paragraphs for explanation.

## Practical Lessons (From Real Cleanup Sessions)

### Lesson 1: Bat File Encoding — The #1 Cause of Flash-Close
Bat files written by PowerShell can be silently corrupted:
- Out-File -Encoding default → ANSI/GBK (works but locale-dependent)
- [System.IO.File]::WriteAllText(path, content, [Text.Encoding]::Unicode) → **UTF-16LE** — cmd.exe crashes on this!
- [System.IO.File]::WriteAllText(path, content, [Text.Encoding]::ASCII) → **Safe**. Pure ASCII works on every Windows system.
- **Rule of thumb**: If a bat file has no Chinese/Unicode text, **always write it as ASCII**. If it must have Unicode text, write as .ps1 (PowerShell) instead.

Detection:
`powershell
# Check first 2 bytes for BOM
 = New-Object byte[] 2
 = [System.IO.File]::OpenRead()
.Read(, 0, 2) | Out-Null; .Close()
if ([0] -eq 0xFF -and [1] -eq 0xFE) {
    "UTF-16LE — cmd.exe will flash-close!"
}
`

### Lesson 2: sc config Syntax Trap
The Windows sc.exe command **requires a space** between the parameter name and value:
`atch
REM CORRECT (with space):
sc config ServiceName start= disabled

REM WRONG (no space — silently fails):
sc config ServiceName start=disabled
`
The space after = is NOT optional. sc.exe treats start= as a flag and disabled (with a leading space) as its value. Without the space, sc.exe sees start=disabled as a single unknown token.

### Lesson 3: The Process Killing Cascade (Correct Order)
When disabling a service-backed process:
`atch
REM Step 1: Stop the service (kills children)
net stop ServiceName

REM Step 2: Disable the service (prevents rebirth)
sc config ServiceName start= disabled

REM Step 3: Kill remaining child processes (if any)
taskkill /f /im ChildProcess.exe /t
`
**Wrong order**: Killing children first just makes the service restart them (thrashing).

### Lesson 4: The 2-Second Rebirth Test
To confirm whether a process is protected by a service:
`atch
REM 1. Count current processes
tasklist /fi "IMAGENAME eq Suspect.exe" | find /c "Suspect.exe"

REM 2. Kill them
taskkill /f /im Suspect.exe /t

REM 3. Wait 2 seconds, count again
timeout /t 2 /nobreak >nul
tasklist /fi "IMAGENAME eq Suspect.exe" | find /c "Suspect.exe"

REM If count is the same → it's a service-controlled process (must use sc config)
`

### Lesson 5: Isolating GPU vs CPU Heat Sources
When the user reports "fan noise even at idle":
1. Check CPU clock: powercfg /getactivescheme should show a throttled plan.
2. Check GPU clock: 
vidia-smi — if the GPU clock is >1000MHz at idle, something is keeping it awake.
3. Check GPU processes: 
vidia-smi --query-compute-apps=pid,process_name --format=csv
4. Common GPU idle blockers: NVIDIA Overlay (5 processes), Electron apps (Cursor, Discord, Slack), browsers with hardware acceleration, dynamic wallpapers.
5. Fix hierarchy: Kill app → if it respawns, it's a service → disable service (Lesson 3) → if still hot, check external monitor (Lesson 6).

### Lesson 6: External Monitor GPU Lock
A monitor plugged into the laptop's HDMI/DP port may be hardwired to the discrete GPU (common on gaming laptops). When an external monitor is connected, the discrete GPU **cannot enter its lowest power state** regardless of software settings. The only fixes:
- Plug the monitor into a USB-C/Thunderbolt port that routes through the integrated GPU.
- Or in NVIDIA Control Panel → Configure Surround, PhysX → set the monitor to use the Intel GPU (rarely supported).
- Or physically disconnect the external monitor when not gaming.

### Lesson 7: The >nul Trap
Redirecting ALL output to >nul 2>&1 makes debugging impossible. When a bat fails:
- User sees [3/4] Cleaning... → then silence → then Done!
- They don't know which command failed or why.
**Rule**: Only suppress output for commands you've verified work. Leave visible output for commands that might fail (especially sc config, 
et stop, del).

### Lesson 8: Service START Values
`	ext
0x00 = BOOT (kernel driver, loaded by OS loader)
0x01 = SYSTEM (kernel driver, loaded during kernel init)
0x02 = AUTOMATIC (started at boot)
0x03 = MANUAL (started on demand)
0x04 = DISABLED (cannot be started)
`
Useful when reading sc qc ServiceName output:
`atch
sc query MarvisSvr | findstr "STATE"
sc qc MarvisSvr | findstr "START_TYPE"
`

### Lesson 9.1: Git Objects as Space Hogs
On developer machines, .git/objects can reach 10-50GB.
- Fix: `git gc --aggressive`
- NEVER delete .git without confirmation.

### Lesson 9.2: MAX_PATH Safe Deletion
Windows 260-char limit. `del /f /s /q` fails silently on deep paths.
- Use PowerShell Remove-Item -Recurse -Force (handles long paths)
- Pre-check: Get-ChildItem $target -Recurse -Name | Where-Object Length -gt 240

### Lesson 9.3: Cross-Drive Move = Copy + Delete
Move-Item C: -> D: is COPY then DELETE. 11GB takes ~20-60s on SSD.
Data exists on BOTH drives temporarily. Check D: free space first.

### Lesson 9.4: Disk Space Update Delay
After deleting, Explorer shows stale free space for 10-30s.
Accurate check: `Get-PSDrive C` or `fsutil volume diskfree C:`

### Lesson 9.5: Inverse Problem Check
After each fix, verify: (1) original symptom resolved, (2) no new symptoms.

### Lesson 9: The "Read-Only" Principle
When reading user data (SQLite databases, config files, logs):
- Always open with 
ead-only mode (open() without write flags, SQLite with SQLITE_OPEN_READONLY).
- Never write to the user's application database — it may corrupt the application's state.
- If you need to persist data, write to a **separate** file (.api_usage_data.json, not state_5.sqlite).

### Lesson 10: The Diagnostic Loop (Scientific Method)
For multi-cause problems (like fan noise):
`
1. OBSERVE: What is the symptom?
2. HYPOTHESIZE: What is the root cause?
3. PREDICT: What should happen if correct?
4. TEST: Change ONE variable
5. MEASURE: Re-check the metric
6. VERIFY or REJECT (process count, CPU temp, GPU temp, C: free space)
2. Change ONE variable (kill Marvis, switch power plan, disable overlay)
3. Measure again — did the metric change? By how much?
4. If yes → confirm the fix. If no → revert and try next variable.
5. Never change two variables at once — you won't know which one worked.
`
This is the scientific method applied to system cleanup. It prevents the "I tried everything and it's still slow" problem.

### Lesson 11: Priority Escalation
Not all cleanup targets are equal. When there's limited time/attention:
`
P0 — System stability (pagefile=0, C drive <10% free)
P1 — Performance (Marvis 10 processes, NVIDIA Overlay locked GPU)
P2 — Space recovery (WeChat 11GB cache, Desktop clutter)
P3 — Convenience (API monitoring dashboard, wallpaper optimization)
`
Always resolve P0 before touching P1, etc.
