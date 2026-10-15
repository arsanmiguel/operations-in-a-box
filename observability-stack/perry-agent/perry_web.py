#!/usr/bin/env python3
"""
Perry the Agent - web view. Renders the latest remediation plan as a shiny
HTML page. Private by default: binds 127.0.0.1 only, reached via SSM tunnel.
Can also regenerate the plan on demand (POST /run).
"""
import json, os, subprocess
from flask import Flask, Response, request, redirect

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_JSON = "/opt/planner/latest_plan.json"
app = Flask(__name__)

TIER_COLOR = {"easy":"#2e9e5b","medium":"#d98a00","advanced":"#c0392b"}

def render():
    if not os.path.exists(PLAN_JSON):
        return "<h2>No plan yet. Run <code>agent.py plan</code> or click Regenerate.</h2>"
    p = json.load(open(PLAN_JSON))
    tiers = p.get("tiers", {})
    total = p.get("total_estimated_monthly_savings", 0)
    r = p.get("self_remediation_request", {})
    def tier_block(name):
        items = tiers.get(name, [])
        rows = "".join(
            f"<tr><td>{i.get('resource','')}</td><td>{i.get('action','')}</td>"
            f"<td style='text-align:right'>${i.get('est_monthly_savings',0)}/mo</td></tr>"
            for i in items)
        return (f"<h3 style='color:{TIER_COLOR.get(name)}'>{name.upper()} "
                f"<span style='font-weight:400;color:#888'>({len(items)})</span></h3>"
                f"<table>{rows or '<tr><td colspan=3 style=color:#888>none</td></tr>'}</table>")
    findings = p.get("_findings", [])
    live = sum(1 for f in findings if f.get("source")=="live")
    samp = sum(1 for f in findings if f.get("source")=="sample")
    # Perry state: cold stare (grayscale, still) when idle; full-color + rescue glow when savings found
    rescue = float(total or 0) > 0
    b64_path = os.path.join(HERE, "perry-b64.txt")
    perry_b64 = open(b64_path).read().strip() if os.path.exists(b64_path) else ""
    svg_path = os.path.join(HERE, "perry-logo.svg")
    perry_svg = open(svg_path).read() if (not perry_b64 and os.path.exists(svg_path)) else ""
    perry_img = (f'<img src="data:image/webp;base64,{perry_b64}" alt="Perry the Agent" '
                 f'class="perry {"rescue" if rescue else "watching"}">') if perry_b64 else (
        f'<div class="perry {"rescue" if rescue else "watching"}" style="height:120px">{perry_svg}</div>' if perry_svg else "")
    mood = "ON THE CASE" if rescue else "watching..."
    html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>Perry the Agent - Remediation Plan</title>
<meta http-equiv=refresh content=30>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:30px auto;padding:0 20px;color:#1a1a1a}}
.hero{{background:linear-gradient(135deg,#1b2a4a,#2e9e5b);color:#fff;border-radius:14px;padding:28px;margin-bottom:24px}}
.big{{font-size:52px;font-weight:800;line-height:1}}
.sub{{opacity:.85;margin-top:6px}}
table{{width:100%;border-collapse:collapse;margin:8px 0 20px}}
td,th{{padding:8px 10px;border-bottom:1px solid #eee;font-size:14px}}
.ask{{background:#f6f8fb;border-left:4px solid #1b2a4a;border-radius:8px;padding:16px 18px;margin:18px 0}}
.pill{{display:inline-block;background:#eef;border-radius:12px;padding:2px 10px;font-size:12px;margin-right:6px}}
.oneliner{{font-size:17px;font-style:italic;background:#fffbe6;border-radius:8px;padding:14px 16px}}
code{{background:#f0f0f0;padding:1px 5px;border-radius:4px}}
form{{display:inline}}
button{{background:#1b2a4a;color:#fff;border:0;border-radius:8px;padding:9px 16px;cursor:pointer}}
.hero{{position:relative;overflow:hidden}}
.perry{{position:absolute;top:14px;right:16px;height:120px;width:auto;border-radius:10px}}
.perry.watching{{filter:grayscale(1) contrast(1.05) brightness(.9);opacity:.85}}
.perry.rescue{{filter:drop-shadow(0 0 16px #ffd34d) saturate(1.1);animation:bob 2.2s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0) rotate(-1deg)}}50%{{transform:translateY(-6px) rotate(1deg)}}}}
</style></head><body>
<div class=hero>
  {perry_img}
  <div style="opacity:.8;letter-spacing:2px;font-size:12px">PERRY THE AGENT &middot; <span style="color:#ffd34d">{mood}</span></div>
  <div class=big>${total}/mo</div>
  <div class=sub>monthly savings identified &middot; {live} live finding(s), {samp} sample &middot; generated {p.get('_generated_at','')}</div>
</div>
<p class=oneliner>{p.get('operator_oneliner','')}</p>
{tier_block('easy')}{tier_block('medium')}{tier_block('advanced')}
<div class=ask>
  <b>Scoped autonomy request</b><br>
  <span class=pill>ask</span>{r.get('summary','')}<br>
  <span class=pill>scope</span>{r.get('scope','')}<br>
  <span class=pill>would do</span>{'; '.join(r.get('easy_actions',[]))}<br>
  <span class=pill>savings if approved</span>${r.get('projected_savings_if_approved',0)}/mo<br>
  <span class=pill>will NOT touch</span>{'; '.join(r.get('what_i_will_NOT_touch',[]))}
</div>
<form method=post action=/run><button>Regenerate plan</button></form>
<p style="color:#aaa;font-size:12px">Private page, served over SSM tunnel. Auto-refreshes every 30s.</p>
</body></html>"""
    return html

@app.route("/")
def index():
    return Response(render(), mimetype="text/html")

@app.route("/run", methods=["POST"])
def run():
    subprocess.run(["python3", os.path.join(HERE,"agent.py"), "plan",
                    "Build a tiered remediation plan for extended support and cost with savings and a scoped autonomy ask."],
                   env={**os.environ,"AWS_REGION":"us-east-1"}, timeout=120)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8088)
