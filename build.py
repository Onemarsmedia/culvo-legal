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
<a href="../privacy/">Privacy policy</a> · <a href="../terms/">Terms of use</a> · <a href="../support/">Support</a></footer>
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

# Support page (App Store "Support URL"). Plain copy, kept in step with docs/launch/05_Support_Page.md.
free = values["Store.freeDeletesPerDay"]
email = values["contactEmail"]
SUPPORT = [
    ("Need a hand?", f'Email <a href="mailto:{email}">{email}</a>. We usually reply within 2 working days.'),
    ("Does Culvo upload my photos?", "No. Everything happens on your iPhone. Your photos never leave it."),
    ("I deleted something by mistake.", "Open the Photos app, go to Albums, then Recently Deleted. iOS keeps deleted photos there for 30 days, and you can restore them from there."),
    ("Why does Culvo need access to my photos?", "To show them to you one by one. With limited access, Culvo can only sort the photos you have selected."),
    ("Is Culvo free?", f"You can delete up to {free} photos a day for free. Culvo Pro removes the limit: £24.99 a year with a 7 day free trial, or £4.99 a month."),
    ("How do I cancel my subscription?", "Open Settings on your iPhone, tap your name, then Subscriptions, then Culvo, then Cancel Subscription."),
    ("Is there a weekly plan?", "No, and there never will be."),
]
(SITE / "support").mkdir(exist_ok=True)
(SITE / "support" / "index.html").write_text(PAGE.format(
    title="Support",
    body="\n".join(f"<h2>{html.escape(h)}</h2>\n<p>{t}</p>" for h, t in SUPPORT),
    extra="", company=values["company"], updated=updated))

(SITE / "index.html").write_text(
    '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=https://culvo.app">'
    '<title>Culvo</title><a href="https://culvo.app">culvo.app</a>\n')
print("Built privacy/, terms/ and support/")
