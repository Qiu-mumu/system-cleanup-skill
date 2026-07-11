# Fan Noise Diagnosis — Walkthrough

A real-case diagnosis following the Decision Tree in this skill.

## Step 1: Observe
User reports: "Fans spin loudly even when I'm not doing anything."

## Step 2: Measure
CPU: i7-14650HX, max clock 2200 MHz (capped by 静音模式 power plan)
GPU: RTX 5060 — 65°C / 17W / 2010 MHz clock (max is 3090 MHz)

## Step 3: Decision Tree
Check CPU frequency -> <2.2GHz (throttled correctly) -> check GPU
  -> GPU >1000MHz (locked at 2010 MHz!)
    -> Check NVIDIA processes: 5 NVIDIA Overlay instances running
    -> Rebirth test: kill overlay -> 2s later, 5 instances back
    -> Service confirmed: NvContainerLocalSystem auto-restarts
    -> Solution: uninstall NVIDIA App (not the driver)

## Step 4: Result
After uninstalling NVIDIA App:
- Overlay processes: 5 -> 0
- GPU temperature: 65°C -> expected <40°C
- Fan noise: eliminated
