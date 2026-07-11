"""report.py — Generate standalone HTML cleanup report with charts."""
import json, os, subprocess, sys
from .cleanup import load_config, scan
from .diagnose import gpu, disk
from .snapshot import load_snapshot

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>System Cleanup Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4">function setLang(l){document.documentElement.lang=l;document.querySelectorAll('.lang-toggle a').forEach(function(a){a.className=a.id=='btn-'+l?'active':''});}
(function(){var l=navigator.language||"";setLang(l.startsWith("zh")?"zh":"en");})();
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;background:#0f1117;color:#e4e6eb;padding:24px}
h1{font-size:22px;margin-bottom:4px}
.sub{color:#8b8fa3;font-size:13px;margin-bottom:20px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.card{background:#1a1d29;border-radius:10px;padding:16px;border:1px solid #252836}
.card .l{color:#8b8fa3;font-size:12px}
.card .v{font-size:26px;font-weight:700;margin-top:4px}
.c1 .v{color:#4ade80} .c2 .v{color:#60a5fa} .c3 .v{color:#fbbf24} .c4 .v{color:#f87171}
.chart-box{background:#1a1d29;border-radius:10px;padding:20px;border:1px solid #252836;margin-bottom:20px}
.chart-box h3{color:#8b8fa3;font-size:14px;margin-bottom:12px}
.chart-box canvas{max-height:280px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:#8b8fa3;font-weight:500;padding:8px 10px;border-bottom:1px solid #252836}
td{padding:6px 10px;border-bottom:1px solid #1f2233}
tr:hover td{background:#1f2233}
.tag{display:inline-block;border-radius:4px;padding:2px 8px;font-size:11px}
.tag-s{background:#1a3a2a;color:#4ade80}
.tag-l{background:#3a2a1a;color:#fbbf24}
.tag-m{background:#3a1a1a;color:#f87171}
.tag-h{background:#3a1a3a;color:#e879f9}
.footer{text-align:center;color:#525668;font-size:12px;margin-top:20px}
@media(max-width:700px){.cards{grid-template-columns:repeat(2,1fr)}}
.lang-toggle{text-align:right;margin-bottom:12px;font-size:13px}
.lang-toggle a{cursor:pointer;color:#60a5fa;text-decoration:none;margin:0 6px}
.lang-toggle a.active{color:#e4e6eb;font-weight:700}
[lang="zh"] .en{display:none}
[lang="en"] .zh{display:none}
.comp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;margin-top:12px}
.delta{font-size:13px;margin-top:4px}
.delta .up{color:#4ade80} .delta .down{color:#f87171}
</style></head>
<body>

<div class="lang-toggle">
  <a class="active" onclick="setLang('zh')" id="btn-zh">中文</a>
  <a onclick="setLang('en')" id="btn-en">English</a>
</div>
<h1><span class="zh">系统清理报告</span><span class="en">System Cleanup Report</span></h1>
<div class="sub">Generated: TIMESTAMP_PLACEHOLDER</div>

<div class="cards">
  <div class="card c1"><div class="l"><span class="zh">可回收</span><span class="en">Recoverable</div><div class="v">TOTAL_GB_PLACEHOLDER GB</div><div class="sub" style="color:#525668;font-size:11px">TOTAL_ITEMS_PLACEHOLDER items found</div></div>
  <div class="card c2"><div class="l"><span class="zh">安全清理</span><span class="en">Safe to Clean</div><div class="v">SAFE_COUNT_PLACEHOLDER</div><div class="sub" style="color:#525668;font-size:11px">SAFE_GB_PLACEHOLDER GB</div></div>
  <div class="card c3"><div class="l"><span class="zh">待复核</span><span class="en">Needs Review</div><div class="v">MEDIUM_COUNT_PLACEHOLDER</div><div class="sub" style="color:#525668;font-size:11px">MEDIUM_GB_PLACEHOLDER GB</div></div>
  <div class="card c4"><div class="l"><span class="zh">C盘</span><span class="en">Disk C:</div><div class="v">DISK_FREE_PLACEHOLDER GB</div><div class="sub" style="color:#525668;font-size:11px">DISK_PCT_PLACEHOLDER% used</div></div>
</div>

SNAPSHOT_HTML_PLACEHOLDER
GPU_STATUS_PLACEHOLDER

<div class="chart-box"><h3>Top Junk by Size (GB)</h3><canvas id="chart"></canvas></div>

<div class="chart-box" style="overflow-x:auto"><h3><span class="zh">全部项目</span><span class="en">All Items</h3>
<table><thead><tr><th><span class="zh">分类</span><span class="en">Category</th><th><span class="zh">路径</span><span class="en">Path</th><th><span class="zh">大小</span><span class="en">Size</th><th><span class="zh">风险</span><span class="en">Risk</th><th><span class="zh">状态</span><span class="en">Status</th></tr></thead>
<tbody>TABLE_ROWS_PLACEHOLDER</tbody></table></div>

<div class="footer">
  <span class="tag tag-s">safe</span>
  <span class="tag tag-l">low</span>
  <span class="tag tag-m">medium</span>
  <span class="tag tag-h">high</span>
  &nbsp;&nbsp;|&nbsp;&nbsp;Run: <code>scl clean</code> to clean safe items
</div>

<script>
const labels = LABELS_PLACEHOLDER;
const data_gb = DATA_GB_PLACEHOLDER;
const colors = COLORS_PLACEHOLDER;

new Chart(document.getElementById('chart'), {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: 'GB',
      data: data_gb,
      backgroundColor: colors,
      borderWidth: 0,
      borderRadius: 4
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color:'#8b8fa3', font:{size:11} }, grid:{color:'#252836'} },
      y: { ticks: { color:'#e4e6eb', font:{size:11} }, grid:{display:false} }
    }
  }
});
function setLang(l){document.documentElement.lang=l;document.querySelectorAll('.lang-toggle a').forEach(function(a){a.className=a.id=='btn-'+l?'active':''});}
(function(){var l=navigator.language||"";setLang(l.startsWith("zh")?"zh":"en");})();
</script>
</body></html>
"""

RISK_COLORS = {"safe":"#4ade8055;#4ade80", "low":"#fbbf2455;#fbbf24",
               "medium":"#f8717155;#f87171", "high":"#e879f955;#e879f9"}
RISK_CLASS = {"safe":"tag-s", "low":"tag-l", "medium":"tag-m", "high":"tag-h"}
RISK_LABEL = {"safe":"safe", "low":"low", "medium":"medium", "high":"high"}

def generate_report(output="system-cleanup-report.html"):
    config = load_config()
    results = scan(config)
    gpu_info = gpu()
    disk_info = disk()

    # Build summary
    total_mb = sum(r["size_mb"] for r in results)
    total_gb = round(total_mb / 1024, 1)
    safe = [r for r in results if r["risk"] == "safe"]
    medium = [r for r in results if r["risk"] in ("low", "medium")]
    safe_gb = round(sum(r["size_mb"] for r in safe) / 1024, 1)
    medium_gb = round(sum(r["size_mb"] for r in medium) / 1024, 1)

    # Disk info
    disk_free = "?"
    disk_pct = "?"
    for d in disk_info:
        if d["drive"] == "C:":
            disk_free = str(d["free"])
            disk_pct = str(d["pct"])

    # GPU status
    # Snapshot comparison
    snap_html = ""
    snap = load_snapshot()
    if snap:
        pc = snap.get("disk_C_free")
        pj = snap.get("junk_total_gb")
        pg = snap.get("gpu_temp")
        st = snap.get("timestamp","?")
        cells = []
        if pc is not None and isinstance(disk_free, (int, float)):
            d = disk_free - pc
            cl = "up" if d>0 else ("down" if d<0 else "same")
            cells.append('<div><span class="zh">C盘</span><span class="en">C Drive</span>:<br>'
                + str(round(pc,1)) + 'GB -> ' + str(round(disk_free,1)) + 'GB<br>'
                + '<span class="delta"><span class="' + cl + '">' + ('+' if d>0 else '') + str(round(d,1)) + 'GB</span></span></div>')
        if pj is not None and isinstance(total_gb, (int, float)):
            d = total_gb - pj
            cl = "down" if d<0 else ("up" if d>0 else "same")
            cells.append('<div><span class="zh">垃圾</span><span class="en">Junk</span>:<br>'
                + str(pj) + 'GB -> ' + str(total_gb) + 'GB<br>'
                + '<span class="delta"><span class="' + cl + '">' + ('+' if d>0 else '') + str(round(d,1)) + 'GB</span></span></div>')
        if pg is not None and "temp" in gpu_info:
            d = gpu_info["temp"] - pg
            cl = "down" if d<0 else ("up" if d>0 else "same")
            cells.append('<div><span class="zh">显卡</span><span class="en">GPU</span>:<br>'
                + str(pg) + 'C -> ' + str(gpu_info["temp"]) + 'C<br>'
                + '<span class="delta"><span class="' + cl + '">' + ('+' if d>0 else '') + str(d) + 'C</span></span></div>')
        if cells:
            joined = "".join(cells)
            snap_html = ("<div class=\"chart-box\" style=\"margin-bottom:20px\"><h3>"
                + '<span class="zh">快照对比</span><span class="en">Since Snapshot</span> (' + st + ')'
                + "</h3><div class=\"comp-grid\">" + joined + "</div></div>")

    gpu_html = ""
    if "temp" in gpu_info:
        flag = "!!! HOT" if gpu_info["temp"] > 60 else ""
        gpu_html = f'<div class="chart-box" style="margin-bottom:20px"><b style="color:#8b8fa3">GPU:</b> {gpu_info["temp"]}C / {gpu_info["power"]}W / {gpu_info["clock"]}MHz <span style="color:{("#4ade80" if gpu_info["temp"]<50 else "#fbbf24" if gpu_info["temp"]<60 else "#f87171")}">{flag}</span></div>'

    # Table rows
    rows = ""
    for r in results:
        risk_c = RISK_CLASS.get(r["risk"], "tag-s")
        sz = f'{r["size_mb"]:.0f} MB' if r["size_mb"] < 1024 else f'{r["size_mb"]/1024:.1f} GB'
        flags = []
        if r["symlink"]: flags.append("symlink")
        if r["locked"]: flags.append("locked")
        if r["fuse"]: flags.append("FUSE")
        status = ", ".join(flags) if flags else "ok"
        st = r["path"][:70] + "..." if len(r["path"]) > 73 else r["path"]
        rows += f'<tr><td>{r["key"][:20]}</td><td style="color:#8b8fa3;font-size:12px">{st}</td>'
        rows += f'<td>{sz}</td><td><span class="tag {risk_c}">{RISK_LABEL.get(r["risk"],"?")}</span></td><td style="color:#525668">{status}</td></tr>\n'

    # Chart data (top 10)
    top = sorted(results, key=lambda x: -x["size_mb"])[:10]
    labels = json.dumps([r["key"][:18] for r in top])
    data_gb = json.dumps([round(r["size_mb"]/1024, 2) for r in top])
    colormap = {"safe":"rgba(74,222,128,0.7)", "low":"rgba(251,191,36,0.7)",
                "medium":"rgba(248,113,113,0.7)", "high":"rgba(232,121,249,0.7)"}
    colors = json.dumps([colormap.get(r["risk"], "rgba(139,143,163,0.7)") for r in top])

    # Build HTML
    html = TEMPLATE
    html = html.replace("TIMESTAMP_PLACEHOLDER", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    html = html.replace("TOTAL_GB_PLACEHOLDER", str(total_gb))
    html = html.replace("TOTAL_ITEMS_PLACEHOLDER", str(len(results)))
    html = html.replace("SAFE_COUNT_PLACEHOLDER", str(len(safe)))
    html = html.replace("SAFE_GB_PLACEHOLDER", str(safe_gb))
    html = html.replace("MEDIUM_COUNT_PLACEHOLDER", str(len(medium)))
    html = html.replace("MEDIUM_GB_PLACEHOLDER", str(medium_gb))
    html = html.replace("DISK_FREE_PLACEHOLDER", disk_free)
    html = html.replace("DISK_PCT_PLACEHOLDER", disk_pct)
    html = html.replace("GPU_STATUS_PLACEHOLDER", gpu_html)
    html = html.replace("TABLE_ROWS_PLACEHOLDER", rows)
    html = html.replace("LABELS_PLACEHOLDER", labels)
    html = html.replace("DATA_GB_PLACEHOLDER", data_gb)
    html = html.replace("COLORS_PLACEHOLDER", colors)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved: {os.path.abspath(output)}")
    try:
        os.startfile(output)
    except:
        pass

def main():
    generate_report()