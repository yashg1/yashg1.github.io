#!/usr/bin/env python3
"""Generate Yash_Ganatra_resume.pdf from resume.json.

Usage: python3 build_pdf.py
Renders a print-optimized HTML version of resume.json, then prints it to PDF
with headless Chrome. Keeps fonts/formatting consistent by construction.
"""
import json
import html
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt(date, default=""):
    if not date:
        return default
    parts = date.split("-")
    if len(parts) >= 2:
        return f"{MONTHS[int(parts[1])]} {parts[0]}"
    return parts[0]


def esc(s):
    return html.escape(s, quote=False)


with open(os.path.join(HERE, "resume.json")) as f:
    r = json.load(f)

b = r["basics"]

jobs = ""
for w in r["work"]:
    bullets = "".join(f"<li>{esc(h)}</li>" for h in w.get("highlights", []))
    jobs += f"""
    <div class="job">
      <div class="job-head">
        <span class="company">{esc(w['company'])}</span>
        <span class="dates">{fmt(w['startDate'])} &ndash; {fmt(w.get('endDate'), 'Present')}</span>
      </div>
      <div class="position">{esc(w['position'])}</div>
      <div class="job-summary">{esc(w.get('summary', ''))}</div>
      <ul>{bullets}</ul>
    </div>"""

edu = ""
for e in r["education"]:
    edu += f"""
    <div class="edu">
      <div class="edu-school">{esc(e['institution'])}</div>
      <div class="edu-degree">{esc(e['studyType'])}, {esc(e['area'])}</div>
      <div class="edu-meta">GPA: {esc(e['gpa'])} &nbsp;|&nbsp; {fmt(e['startDate'])} &ndash; {fmt(e['endDate'])}</div>
    </div>"""

skills = ""
for s in r["skills"]:
    items = "".join(f"<li>{esc(k)}</li>" for k in s["keywords"])
    skills += f"""
    <div class="skill-group">
      <div class="skill-name">{esc(s['name'])}</div>
      <ul>{items}</ul>
    </div>"""

pubs = ""
for p in r["publications"]:
    pubs += f"""
    <div class="pub">
      <a href="{p['website']}">{esc(p['name'])}</a>
      <div class="pub-meta">{esc(p['publisher'])}</div>
    </div>"""

langs = ", ".join(f"{esc(l['language'])} ({esc(l['fluency'])})" for l in r.get("languages", []))

page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Resume of {esc(b['name'])}</title>
<style>
  @page {{ size: letter; margin: 0.38in 0.45in; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9pt; line-height: 1.28; color: #222;
  }}
  a {{ color: #1668b3; text-decoration: none; }}
  header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    border-bottom: 2px solid #00a651; padding-bottom: 6px; margin-bottom: 9px;
  }}
  .name {{ font-size: 18pt; font-weight: 700; color: #00a651; letter-spacing: .3px; }}
  .role {{ font-size: 11pt; font-weight: 600; color: #222; margin-top: 1px; }}
  .contact {{ text-align: right; font-size: 9pt; line-height: 1.4; }}
  .columns {{ display: grid; grid-template-columns: 2.05in 1fr; column-gap: 0.3in; }}
  h2 {{
    font-size: 10.5pt; font-weight: 700; color: #1668b3;
    text-transform: uppercase; letter-spacing: .5px;
    margin: 7px 0 3px; border-bottom: 1px solid #d8d8d8; padding-bottom: 2px;
  }}
  h2:first-child {{ margin-top: 0; }}
  ul {{ list-style: disc; margin-left: 14px; }}
  li {{ margin-bottom: 1.5px; }}
  .sidebar {{ font-size: 8.5pt; }}
  /* sidebar */
  .edu {{ margin-bottom: 6px; }}
  .edu-school {{ font-weight: 700; }}
  .edu-degree {{ }}
  .edu-meta {{ color: #555; font-size: 8.5pt; }}
  .skill-group {{ margin-bottom: 6px; }}
  .skill-name {{ font-weight: 700; margin-bottom: 1px; }}
  .pub {{ margin-bottom: 5px; }}
  .pub a {{ font-weight: 600; }}
  .pub-meta {{ color: #555; font-size: 8.5pt; font-style: italic; }}
  /* main */
  .summary {{ margin-bottom: 2px; }}
  .job {{ margin-bottom: 7px; break-inside: avoid; }}
  .job-head {{
    display: flex; justify-content: space-between; align-items: baseline;
    background: #fbe4d5; border: 1px solid #222; padding: 2px 7px; margin-bottom: 3px;
  }}
  .company {{ font-weight: 700; font-size: 10.5pt; }}
  .dates {{ font-size: 9pt; font-weight: 600; }}
  .position {{ font-weight: 700; margin-bottom: 1px; }}
  .job-summary {{ font-style: italic; margin-bottom: 2px; }}
</style></head>
<body>
  <header>
    <div>
      <div class="name">{esc(b['name'])}</div>
      <div class="role">{esc(b['label'])}</div>
    </div>
    <div class="contact">
      {esc(b['location']['city'])}, {'TX' if b['location']['region'] == 'Texas' else esc(b['location']['region'])}<br>
      LinkedIn: <a href="https://www.linkedin.com/in/yashganatra">yashganatra</a><br>
      <a href="{b['website']}">{b['website'].replace('https://', '')}</a><br>
      <a href="mailto:{b['email']}">{b['email']}</a>
    </div>
  </header>
  <div class="columns">
    <div class="sidebar">
      <h2>Education</h2>{edu}
      <h2>Skills</h2>{skills}
      <h2>Publications</h2>{pubs}
      <h2>Languages</h2><div>{langs}</div>
    </div>
    <div class="main">
      <h2>Summary</h2>
      <div class="summary">{esc(b['summary'])}</div>
      <h2>Professional Experience</h2>
      {jobs}
    </div>
  </div>
</body></html>"""

html_path = os.path.join(tempfile.gettempdir(), "resume_print.html")
with open(html_path, "w") as f:
    f.write(page)

out = os.path.join(HERE, "Yash_Ganatra_resume.pdf")
subprocess.run([
    CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
    f"--print-to-pdf={out}", html_path,
], check=True, capture_output=True)
print("wrote", out)
