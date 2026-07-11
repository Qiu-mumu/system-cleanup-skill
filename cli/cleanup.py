"""cleanup.py — Safe cleanup executor. Reads config.json, checks safety, executes."""
import json, os, subprocess, sys, shutil, platform
from pathlib import Path

HOME = os.path.expanduser("~")
CONFIG = os.path.join(os.path.dirname(__file__), "config.json")
ABSOLUTE_FUSES = [r"C:\Windows\WinSxS", r"C:\Windows\assembly", r"C:\Windows\SideBySide",
                  "pagefile.sys", "hiberfil.sys", "swapfile.sys"]

def expand(path):
    """Expand %USERPROFILE%, %APPDATA%, %LOCALAPPDATA%, %TEMP%, %windir%"""
    p = path.replace("%USERPROFILE%", HOME).replace("%APPDATA%", os.path.join(HOME, "AppData", "Roaming"))
    p = p.replace("%LOCALAPPDATA%", os.path.join(HOME, "AppData", "Local"))
    p = p.replace("%TEMP%", os.path.join(HOME, "AppData", "Local", "Temp"))
    p = p.replace("%windir%", os.environ.get("windir", "C:\\Windows"))
    return p

def is_symlink_or_junction(path):
    """Check if path is a symlink or junction (reparse point)."""
    try:
        if os.path.islink(path): return True
        if os.path.isdir(path):
            out = subprocess.run(["fsutil", "reparsepoint", "query", path],
                                 capture_output=True, text=True, timeout=5)
            return "Reparse Tag" in out.stdout and "Symbolic Link" in out.stdout
    except: pass
    return False

def is_locked(path):
    """Test if file is locked by a running process via open() test."""
    if not os.path.isfile(path): return False
    try:
        with open(path, "a"): pass
        return False
    except (PermissionError, OSError):
        return True

def is_absolute_fuse(path):
    """Check if path matches the absolute fuses list."""
    norm = os.path.normpath(path).lower()
    for fuse in ABSOLUTE_FUSES:
        if fuse.lower() in norm: return True
    return False

def estimate_size(path):
    """Quick size estimation. Stops early for large dirs."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    try:
        for i, (dirpath, _, filenames) in enumerate(os.walk(path)):
            if i > 5000: break  # safety limit
            for f in filenames:
                try: total += os.path.getsize(os.path.join(dirpath, f))
                except: pass
    except: pass
    return total

def load_config():
    with open(CONFIG, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def scan(config):
    """Scan all config entries, checking existence + safety. Returns a list of scan results."""
    results = []
    for key, entry in config.items():
        for raw_path in entry["paths"]:
            path = expand(raw_path)
            if not os.path.exists(path): continue
            size = estimate_size(path)
            sym = is_symlink_or_junction(path)
            locked = any(is_locked(os.path.join(dirpath, f))
                         for dirpath, _, files in os.walk(path) for f in files[:5]) if os.path.isdir(path) else is_locked(path)
            fuse = is_absolute_fuse(path)
            results.append({
                "key": key, "path": path, "size_mb": round(size / 1e6, 1),
                "symlink": sym, "locked": locked, "fuse": fuse,
                "risk": entry.get("risk", "safe"),
                "clean_cmd": entry.get("clean_cmd", ""),
                "desc": entry.get("desc", ""),
                "admin": entry.get("admin_required", False),
            })
    return sorted(results, key=lambda x: -x["size_mb"])

def execute(entry, dry_run=False):
    """Execute cleanup for a single entry."""
    if not entry["clean_cmd"]:
        return f"SKIP: no clean_cmd for {entry['key']}"
    cmd = entry["clean_cmd"]
    # Expand variables in the command
    cmd = cmd.replace("%USERPROFILE%", HOME).replace("%windir%", os.environ.get("windir", "C:\\Windows"))
    if dry_run:
        return f"DRY-RUN: {cmd}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            return f"OK: {entry['key']}"
        else:
            return f"WARN: {entry['key']} exited {r.returncode}: {r.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: {entry['key']}"
    except Exception as e:
        return f"ERROR: {entry['key']}: {e}"

def print_report(results, title="Scan Results"):
    """Print a formatted report table."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    for r in results:
        flags = []
        if r["symlink"]: flags.append("SYMLINK")
        if r["locked"]: flags.append("LOCKED")
        if r["fuse"]: flags.append("FUSE!")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        risk = {"safe": " ", "low": "~", "medium": "?", "high": "!"}.get(r["risk"], "?")
        admin = " [ADMIN]" if r["admin"] else ""
        print(f"  {risk} {r['path'][:55]:55s} {r['size_mb']:>8.1f}MB{flag_str}{admin}")
    print(f"{'='*60}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="System cleanup tool")
    parser.add_argument("mode", nargs="?", default="scan", choices=["scan", "clean", "diagnose"])
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    parser.add_argument("--full", action="store_true", help="Include admin-required operations")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    config = load_config()
    results = scan(config)

    if args.mode == "scan" or args.mode == "diagnose":
        print_report(results)
        total = sum(r["size_mb"] for r in results)
        print(f"  Total: {total:.0f} MB recoverable\n")
        return

    # clean mode
    safe = [r for r in results if not r["fuse"] and not r["symlink"]]
    if not args.full:
        safe = [r for r in safe if not r["admin"]]

    print_report(safe, "Items to clean")

    if not args.yes:
        inp = input("\nProceed? [y/N]: ").strip().lower()
        if inp != "y":
            print("Cancelled.")
            return

    print("\nExecuting...")
    for r in safe:
        if r["locked"]:
            print(f"  SKIP (locked): {r['key']}")
            continue
        result = execute(r, dry_run=args.dry_run)
        print(f"  {result}")

    print("\nDone.")

if __name__ == "__main__":
    main()