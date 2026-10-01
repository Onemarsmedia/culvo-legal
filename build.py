#!/usr/bin/env python3
"""Builds the public privacy policy and terms pages from the text inside the app
(Culvo/Legal.swift), so the website and the app always say the same thing.

Run from the Culvo-app folder:  python3 legal-site/build.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
swift = (ROOT / "Culvo" / "Legal.swift").read_text()
SITE = ROOT / "legal-site"


def constant(name):
    return re.search(rf'static let {name} = "([^"]*)"', swift).group(1)


values = {
    "company": constant("company"),
    "contactEmail": constant("contactEmail"),
    "Store.freeDeletesPerDay": re.search(
        r"freeDeletesPerDay = (\d+)", (ROOT / "Culvo" / "Store.swift").read_text()).group(1),
}
updated = constant("lastUpdated")
eula = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"


def sections(name):
    block = re.search(rf"static let {name}: \[\(String, String\)\] = \[(.*?)\n    \]", swift, re.S).group(1)
    pairs = re.findall(r'\(\s*"([^"]*)",\s*"((?:[^"\\]|\\.)*)"\s*\)', block)
    out = []
    for heading, text in pairs:
        text = re.sub(r"\\\((.*?)\)", lambda m: values[m.group(1)], text)
        text = text.replace('\\"', '"')
        safe = html.escape(text)
        email = values["contactEmail"]
        safe = safe.replace(email, f'<a href="mailto:{email}">{email}</a>')
        out.append(f"<h2>{html.escape(heading)}</h2>\n<p>{safe}</p>")
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Culvo</title>
<style>
  :root {{ --bg: #0B0B0C; --text: #F4F4F2; --muted: rgba(244,244,242,.72); --lime: #C6FF3D; }}
  body {{ margin: 0; background: var(--bg); color: var(--text);
         font: 17px/1.6 ui-rounded, "SF Pro Rounded", -apple-system, system-ui, sans-serif; }}
  main {{ max-width: 680px; margin: 0 auto; padding: 48px 20px 80px; }}
  .mark {{ font-weight: 800; font-size: 28px; letter-spacing: -.5px; text-decoration: none; color: var(--text); }}
  .mark span {{ color: var(--lime); }}
  h1 {{ font-size: 40px; line-height: 1.1; margin: 40px 0 8px; }}
  h2 {{ font-size: 20px; margin: 32px 0 6px; }}
  p {{ color: var(--muted); margin: 0; }}
  a {{ color: var(--lime); }}
  footer {{ margin-top: 48px; color: rgba(244,244,242,.45); font-size: 14px; }}
</style>
</head>
<body>
<main>
<a class="mark" href="https://culvo.app">culvo<span>.</span></a>
<h1>{title}</h1>
{body}
{extra}
<footer>{company} · Last updated {updated}<br>
<a href="../privacy/">Privacy policy</a> · <a href="../terms/">Terms of use</a></footer>
</main>
</body>
</html>
"""

for slug, name, title, extra in [
    ("privacy", "privacy", "Privacy policy", ""),
    ("terms", "terms", "Terms of use", f'<h2>Licence</h2>\n<p><a href="{eula}">Apple\'s standard licence agreement</a></p>'),
]:
    (SITE / slug).mkdir(exist_ok=True)
    (SITE / slug / "index.html").write_text(PAGE.format(
        title=title, body=sections(name), extra=extra, company=values["company"], updated=updated))

(SITE / "index.html").write_text(
    '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=https://culvo.app">'
    '<title>Culvo</title><a href="https://culvo.app">culvo.app</a>\n')
print("Built privacy/ and terms/")
