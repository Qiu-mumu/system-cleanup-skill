"""report_fix.py — Post-process report: inject before/after comparison with current data."""
import os, json

MARKER = "ZZZ_SNAPSHOT_MARKER_ZZZ"

def fix_report():
    path = os.path.expanduser("~/Desktop/system-cleanup-report.html")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if MARKER not in html:
        return

    # Read snapshot (before)
    sf = os.path.expanduser("~/.system-cleanup-snapshot.json")
    if not os.path.exists(sf):
        html = html.replace(MARKER, "")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return

    with open(sf, "r") as f:
        snap = json.load(f)

    # Get current data
    import cli.diagnose
    di = cli.diagnose.disk()
    gi = cli.diagnose.gpu()

    pc = snap.get("disk_C_free")
    pj = snap.get("junk_total_gb")
    pg = snap.get("gpu_temp")
    st = snap.get("timestamp", "?")

    # Get current disk_free (C:)
    cur_free = "?"
    for d in di:
        if d["drive"] == "C:":
            cur_free = d["free"]

    cells = []
    arrow = " -> "

    if pc is not None and isinstance(cur_free, (int, float)):
        d = cur_free - pc
        cl = "up" if d > 0 else ("down" if d < 0 else "same")
        cells.append(
            "<div><span class=\"zh\">C盘</span><span class=\"en\">C Drive</span>:<br>"
            + str(round(pc, 1)) + "GB" + arrow + str(round(cur_free, 1)) + "GB"
            + "<br><span class=\"delta\"><span class=\"" + cl + "\">"
            + ("+" if d > 0 else "") + str(round(d, 1)) + "GB</span></span></div>"
        )

    if pj is not None:
        cells.append(
            "<div><span class=\"zh\">垃圾(快照)</span><span class=\"en\">Junk(snap)</span>:<br>"
            + str(round(pj, 1)) + "GB</div>"
        )

    if pg is not None and "temp" in gi:
        d = gi["temp"] - pg
        cl = "down" if d < 0 else ("up" if d > 0 else "same")
        cells.append(
            "<div><span class=\"zh\">显卡</span><span class=\"en\">GPU</span>:<br>"
            + str(pg) + "C" + arrow + str(gi["temp"]) + "C"
            + "<br><span class=\"delta\"><span class=\"" + cl + "\">"
            + ("+" if d > 0 else "") + str(d) + "C</span></span></div>"
        )

    if cells:
        joined = "".join(cells)
        comp = (
            "<div class=\"chart-box\" style=\"margin-bottom:20px\">"
            + "<h3><span class=\"zh\">快照对比</span><span class=\"en\">Snapshot vs Now</span> (" + str(st) + ")</h3>"
            + "<div class=\"comp-grid\">" + joined + "</div></div>"
        )
        html = html.replace(MARKER, comp)
    else:
        html = html.replace(MARKER, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)