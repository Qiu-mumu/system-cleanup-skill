"""snapshot.py -- Save current system state for before/after comparison."""
import json, os
from .cleanup import load_config, scan
from .diagnose import gpu, disk

SNAPSHOT_FILE = os.path.expanduser("~/.system-cleanup-snapshot.json")

def take_snapshot():
    try:
    config = load_config(); results = scan(config)
    gi = gpu(); di = disk()
    total = round(sum(r["size_mb"] for r in results)/1024, 1)
    snap = {"timestamp": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
            "junk_total_gb": total}
    for d in di: snap["disk_" + d["drive"].strip(":") + "_free"] = d["free"]
    if "temp" in gi: snap["gpu_temp"] = gi["temp"]
    with open(SNAPSHOT_FILE,"w",encoding="utf-8") as fh: json.dump(snap,fh,indent=2)
    print(f"Snapshot saved. C: {snap.get('disk_C_free','?')}GB")

def load_snapshot():
    try:
        with open(SNAPSHOT_FILE,"r",encoding="utf-8") as fh: return json.load(fh)
    except: return None

    except Exception as e:
        print('Snapshot failed: ' + str(e))

def main(): take_snapshot()
