# -*- coding: utf-8 -*-
"""שימי סטודיו v1.5 — דמויות לחיצות + גלריה לכל דמות + היסטוריית רשת מלאה.
אדיטיבי בלבד: לא מוחק כלום. אידמפוטנטי: בטוח להריץ פעמיים."""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.py")
UI = os.path.join(HERE, "ui", "index.html")

app = io.open(APP, encoding="utf-8").read()

if "SHIMI_15" not in app:
    helper = '''
# ── SHIMI_15: היסטוריית רשת (אינדקס 410 תמונות, מקור aidoor) ──
_NET_IDX_URLS = ["https://aidoor.shimi.land/history-index.json",
                 "https://raw.githubusercontent.com/sunraz/shimi-land/main/history-index.json"]
_net_cache = {"t": 0, "items": []}
def _net_history():
    import time, urllib.request
    now = time.time()
    if _net_cache["items"] and now - _net_cache["t"] < 600:
        return _net_cache["items"]
    for u in _NET_IDX_URLS:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "ShimiStudio/1.5"})
            with urllib.request.urlopen(req, timeout=10) as r:
                d = json.loads(r.read().decode("utf-8"))
                _net_cache["t"] = now
                _net_cache["items"] = d.get("items", [])
                return _net_cache["items"]
        except Exception:
            continue
    return []
'''
    anchor = "import characters"
    if anchor not in app:
        print("E: anchor app not found"); sys.exit(1)
    app = app.replace(anchor, anchor + "\n" + helper, 1)

    old_hist = '''        elif p == "/api/history":
            files = sorted(os.listdir(HISTORY), reverse=True)[:100]
            self._send(200, {"files": [f for f in files if f.endswith(".png")]})'''
    new_hist = '''        elif p == "/api/history":
            files = sorted(os.listdir(HISTORY), reverse=True)[:100]
            self._send(200, {"files": [f for f in files if f.endswith(".png")],
                             "items": _net_history()})'''
    if old_hist not in app:
        print("E: history handler not found"); sys.exit(1)
    app = app.replace(old_hist, new_hist, 1)
    io.open(APP, "w", encoding="utf-8").write(app)
    print("app.py מושלם ✔")
else:
    print("app.py כבר מושלם (SHIMI_15)")

ui = io.open(UI, encoding="utf-8").read()

if "SHIMI_15" not in ui:
    old_hdr = '<h2 style="margin-bottom:10px;font-size:1rem">היסטוריה (100 אחרונות)</h2>\n  <div class="results" id="h_list"></div>'
    new_hdr = '''<h2 style="margin-bottom:10px;font-size:1rem">היסטוריה מלאה — רשת שימי + מקומי <select id="h_filter" style="float:left;margin-inline-end:8px"><option value="">הכל</option></select></h2>
  <div class="results" id="h_net"></div>
  <h2 style="margin:14px 0 8px;font-size:.9rem;color:var(--mut)">פלט מקומי</h2>
  <div class="results" id="h_list"></div>
  <div id="char_modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:50;overflow:auto" onclick="if(event.target===this)this.style.display='none'">
    <div style="max-width:1100px;margin:30px auto;padding:0 14px"><div style="display:flex;justify-content:space-between;align-items:center"><h2 id="cm_title" style="color:#fff"></h2><button onclick="document.getElementById('char_modal').style.display='none'" style="background:var(--card);border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px 16px;cursor:pointer">סגור ✕</button></div><div class="results" id="cm_grid"></div></div>
  </div>'''
    if old_hdr not in ui:
        print("E: hist header not found"); sys.exit(1)
    ui = ui.replace(old_hdr, new_hdr, 1)

    old_c = '''  $("c_list").innerHTML=Object.entries(STATE.characters||{}).map(([k,v])=>`
    <div class="panel ${v.locked?"locked":""}"><h2>${v.label}</h2><p style="font-size:.82rem;color:var(--mut)">${v.desc}</p>
    ${v.locked?'<p style="font-size:.75rem;color:var(--bad);margin-top:8px">חסומה עד אישור מפרט מסאן</p>':""}</div>`).join("");'''
    new_c = '''  $("c_list").innerHTML=Object.entries(STATE.characters||{}).map(([k,v])=>`
    <div class="panel ${v.locked?"locked":""}" style="cursor:pointer" data-char="${v.label}" onclick="openCharGallery('${v.label}')"><h2>${v.label} <span style="font-size:.72rem;color:var(--mut)">תמונות: ${charCounts[v.label]||0} ← לחץ לצפייה</span></h2><p style="font-size:.82rem;color:var(--mut)">${v.desc}</p>
    ${v.locked?'<p style="font-size:.75rem;color:var(--bad);margin-top:8px">חסומה עד אישור מפרס מסאן</p>':""}</div>`).join("");'''
    if old_c not in ui:
        print("E: chars block not found"); sys.exit(1)
    ui = ui.replace(old_c, new_c, 1)

    old_lh = '''async function loadHistory(){
  const h=await api("/api/history");
  $("h_list").innerHTML=(h.files||[]).map(f=>`<div class="card"><img src="/history/${f}" loading="lazy"><div class="meta">${f}</div></div>`).join("");
}'''
    new_lh = '''let NET_ITEMS=[],charCounts={};
async function loadHistory(){
  const h=await api("/api/history");
  $("h_list").innerHTML=(h.files||[]).map(f=>`<div class="card"><img src="/history/${f}" loading="lazy"><div class="meta">${f}</div></div>`).join("");
  NET_ITEMS=(h.items||[]);
  const counts={};NET_ITEMS.forEach(i=>counts[i.char]=(counts[i.char]||0)+1);
  const labels=new Set(Object.values(STATE.characters||{}).map(v=>v.label));labels.add("כללי");
  charCounts=Object.fromEntries(Object.entries(counts).filter(([k])=>labels.has(k)));
  const fs=$("h_filter");if(fs&&!fs.dataset.on){fs.dataset.on="1";fs.innerHTML='<option value="">הכל</option>'+[...labels].map(l=>`<option value="${l}">${l}</option>`).join("");fs.onchange=()=>renderNet();}
  if(typeof STATE!=="undefined")renderCharsWithCounts();
  renderNet();
}
function renderNet(){
  const f=$("h_filter")?$("h_filter").value:"";
  const items=NET_ITEMS.filter(i=>!f||i.char===f);
  $("h_net").innerHTML=items.map(i=>`<div class="card"><a href="${i.url}" target="_blank"><img src="${i.url}" loading="lazy" style="width:100%;display:block"></a><div class="meta">${i.char} · ${i.folder} · ${i.title}</div></div>`).join("")||'<p style="color:var(--mut)">אין תוצאות</p>';
}
function openCharGallery(label){
  const items=NET_ITEMS.filter(i=>i.char===label);
  $("cm_title").textContent=label+" — כל התמונות שיצרנו ("+items.length+")";
  $("cm_grid").innerHTML=items.map(i=>`<div class="card"><a href="${i.url}" target="_blank"><img src="${i.url}" loading="lazy" style="width:100%;display:block"></a><div class="meta">${i.folder} · ${i.title}</div></div>`).join("")||'<p style="color:#fff">אין עדיין תמונות לדמות זו באינדקס</p>';
  $("char_modal").style.display="block";
}
function renderCharsWithCounts(){
  $("c_list").innerHTML=Object.entries(STATE.characters||{}).map(([k,v])=>`
    <div class="panel ${v.locked?"locked":""}" style="cursor:pointer" onclick="openCharGallery('${v.label}')"><h2>${v.label} <span style="font-size:.72rem;color:var(--mut)">תמונות: ${charCounts[v.label]||0} ← לחץ לצפייה</span></h2><p style="font-size:.82rem;color:var(--mut)">${v.desc}</p>
    ${v.locked?'<p style="font-size:.75rem;color:var(--bad);margin-top:8px">חסומה עד אישור מפרס מסאן</p>':""}</div>`).join("");
}'''
    if old_lh not in ui:
        print("E: loadHistory not found"); sys.exit(1)
    ui = ui.replace(old_lh, new_lh, 1)
    ui = ui.replace("const $=id=>", "// SHIMI_15\nconst $=id=>", 1)
    io.open(UI, "w", encoding="utf-8").write(ui)
    print("index.html מושלם ✔")
else:
    print("index.html כבר מושלם (SHIMI_15)")
print("PATCH15_DONE")
