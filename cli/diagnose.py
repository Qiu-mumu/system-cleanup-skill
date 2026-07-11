"""diagnose.py - System health diagnosis. Usage: python diagnose.py [--json]"""
import subprocess, shutil, json, os, sys
from datetime import datetime
HOME = os.path.expanduser("~")

def run(cmd, t=10):
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=t); return r.stdout.strip()
    except: return ""

def disk():
    r=[]
    for d in ["C:","D:"]:
        try:
            t,u,f = shutil.disk_usage(d+"\\")
            r.append({"drive":d,"total":round(t/1e9,1),"free":round(f/1e9,1),"pct":round(u/t*100,1)})
        except: pass
    return r

def gpu():
    o = run(["nvidia-smi","--query-gpu=temperature.gpu,utilization.gpu,power.draw,clocks.current.graphics","--format=csv,noheader"],5)
    if not o: return {"error":"nvidia-smi not found"}
    p = [x.strip() for x in o.split(",")]
    try: return {"temp":int(p[0]),"util":int(p[1].replace("%","")),"power":float(p[2].replace("W","")),"clock":int(p[3].replace(" MHz",""))}
    except: return {"raw":o}

def processes():
    bad = ["MarvisKnowledgebase","MarvisHost","NVIDIA Overlay","nano"]
    r=[]
    for n in bad:
        o=run(["tasklist","/fi",f"IMAGENAME eq {n}.exe"],5)
        c=o.count(n)
        if c: r.append({"name":n,"count":c})
    return r

def large():
    targets = [os.path.join(HOME,".cache"),os.path.join(HOME,"AppData","Local","Temp"),
               os.path.join(HOME,"AppData","Local","pip","cache"),os.path.join(HOME,"AppData","Roaming","Tencent"),
               os.path.join(HOME,".android"),os.path.join(HOME,".gradle")]
    r=[]
    for p in targets:
        if os.path.exists(p):
            s=0
            try:
                for a,_,b in os.walk(p):
                    for f in b:
                        try: s+=os.path.getsize(os.path.join(a,f))
                        except: pass
            except: pass
            if s>1e8: r.append({"path":p.replace(HOME,"~"),"mb":round(s/1e6,1)})
    return sorted(r,key=lambda x:-x["mb"])

def main():
    js="--json" in sys.argv
    g=gpu(); d=disk(); p=processes(); l=large()[:8]
    if js:
        print(json.dumps({"time":str(datetime.now()),"disk":d,"gpu":g,"problems":p,"large":l},indent=2))
        return
    print("="*50)
    print("  System Diagnosis - $(date)")
    print("="*50)
    for x in d: print(f"  {x['drive']}: {x['free']}GB free ({x['pct']}% used)"+(" ***" if x['free']<10 else ""))
    if "temp" in g: print(f"  GPU: {g['temp']}C / {g['power']}W / {g['clock']}MHz"+(" ***" if g['temp']>60 else ""))
    else: print(f"  GPU: {g.get('error','?')}")
    if p:
        print("  !! Problems:", ", ".join(f"{x['name']}(x{x['count']})" for x in p))
    if l:
        print("  Large dirs:")
        for x in l: print(f"    {x['path']}: {x['mb']}MB")

if __name__=="__main__": main()
