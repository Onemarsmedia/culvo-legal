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
    "companyDetails": constant("companyDetails"),
    "Store.freeBiggestTaster": re.search(
        r"freeBiggestTaster = (\d+)", (ROOT / "Culvo" / "Store.swift").read_text()).group(1),
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
  a {{ color: var(--lime); text-underline-offset: 3px; }}
  a:focus-visible {{ outline: 3px solid var(--lime); outline-offset: 3px; border-radius: 4px; }}
  .skip {{ position: absolute; left: -999px; top: 8px; background: var(--lime); color: #0B0B0C; padding: 8px 12px; border-radius: 8px; font-weight: 700; }}
  .skip:focus {{ left: 12px; }}
  footer {{ margin-top: 48px; color: rgba(244,244,242,.72); font-size: 14px; line-height: 1.9; }}
</style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header><a class="mark" href="https://culvo.app" aria-label="Culvo home">culvo<span aria-hidden="true">.</span></a></header>
<main id="content">
<h1>{title}</h1>
{body}
{extra}
</main>
<footer>{company_details}<br>Last updated {updated}<br>
<nav aria-label="Legal"><a href="../privacy/">Privacy</a> · <a href="../terms/">Terms</a> · <a href="../refunds/">Refunds</a> · <a href="../cookies/">Cookies</a> · <a href="../accessibility/">Accessibility</a> · <a href="../support/">Support</a> · <a href="../updates/">Updates</a></nav></footer>
</body>
</html>
"""

for slug, name, title, extra in [
    ("privacy", "privacy", "Privacy policy", ""),
    ("terms", "terms", "Terms of use", f'<h2>Licence</h2>\n<p><a href="{eula}">Apple\'s standard licence agreement</a></p>'),
    ("refunds", "refunds", "Cancellations and refunds", ""),
    ("cookies", "cookies", "Cookie policy", ""),
    ("accessibility", "accessibility", "Accessibility", ""),
]:
    (SITE / slug).mkdir(exist_ok=True)
    (SITE / slug / "index.html").write_text(PAGE.format(
        title=title, body=sections(name), extra=extra, company=values["company"], company_details=html.escape(values["companyDetails"]), updated=updated))

# Support page (App Store "Support URL"). Plain copy, kept in step with docs/launch/05_Support_Page.md.
email = values["contactEmail"]
SUPPORT = [
    ("Need a hand?", f'Email <a href="mailto:{email}">{email}</a>. We usually reply within 2 working days.'),
    # Using Culvo
    ("What is Culvo?", "An iPhone app that cleans your camera roll by swiping. Post it or toss it."),
    ("How does it work?", "Culvo shows your photos one at a time, newest first. Swipe right to keep, left to toss. Tossed photos wait in a toss pile until you delete them, and Undo takes back your last swipe."),
    ("What is Biggest first?", "Biggest first shows your largest photos and videos first, so a few swipes clear the most space. Free users can try the first 10 cards; the rest is part of Culvo Pro."),
    ("What is Similar?", "Similar finds bursts and near-identical shots, like the 12 photos you took to get one good one. Culvo picks the best shot on your iPhone, and you choose to keep the best and toss the rest. Part of Culvo Pro."),
    ("What is Ready to post?", "Everything you keep goes into a “Culvo – Ready to post” album in your Photos app, so your keepers are in one place. In Culvo Pro you can pick some and share them straight to Instagram, TikTok or anywhere else."),
    ("I deleted photos but my storage didn't change.", "iOS keeps deleted photos in Recently Deleted for 30 days. Open Photos, tap Collections, then Recently Deleted, then Select and Delete All to get the space back. Culvo shows these steps after every delete."),
    ("Can I clear out just screenshots?", "Yes. Tap Screenshots at the top to sort only your screenshots: receipts, memes, old chats."),
    ("Will Culvo remember where I left off?", "Yes. Photos you've already sorted don't come back, and your toss pile is saved. When you've been through everything, tap Start over to go again."),
    # Your photos
    ("Does Culvo upload my photos?", "No. Culvo sorts everything on your iPhone and never uploads your photos. (If you use iCloud Photos, Apple syncs them as usual.)"),
    ("Will Culvo delete anything without asking?", "Never. Nothing is deleted until you tap Delete, and iOS always shows its own confirmation first."),
    ("I deleted something by mistake.", "Open the Photos app, go to Albums, then Recently Deleted. iOS keeps deleted photos there for 30 days, and you can restore them from there."),
    ("I use iCloud Photos. Anything I should know?", "Culvo works with iCloud Photos, and photos stored only in iCloud are downloaded so you can see them. Deleting a photo removes it from every device that uses iCloud Photos, just like deleting it in the Photos app."),
    ("Why does Culvo need access to my photos?", "To show them to you one by one. With limited access, Culvo can only sort the photos you have selected."),
    # Culvo Pro
    ("Is Culvo free?", "Yes. Swiping and deleting are free with no daily limit. Culvo Pro adds Biggest first, Best of the burst and Ready to post: £24.99 a year with a 7 day free trial, or £4.99 a month."),
    ("How do I cancel my subscription?", "Open Settings on your iPhone, tap your name, then Subscriptions, then Culvo, then Cancel Subscription."),
    ("I already paid. How do I get Pro back on a new phone?", "In Culvo, tap the culvo. logo at the top, then Restore purchases."),
    ("Is there a weekly plan?", "No, and there never will be."),
    # Availability
    ("Which iPhones does Culvo work on?", "Any iPhone with iOS 18 or later."),
    ("Is there an Android version?", "Not yet. Culvo is iPhone only for now."),
    ("When can I get Culvo?", 'Culvo is in testing. Join the waitlist at <a href="https://culvo.app">culvo.app</a> and we\'ll let you know.'),
]
(SITE / "support").mkdir(exist_ok=True)
(SITE / "support" / "index.html").write_text(PAGE.format(
    title="Support &amp; FAQ",
    body="\n".join(f"<h2>{html.escape(h)}</h2>\n<p>{t}</p>" for h, t in SUPPORT),
    extra="", company=values["company"], company_details=html.escape(values["companyDetails"]), updated=updated))

# Updates page, from the same list the app shows in About > What's new (Culvo/Updates.swift).
updates_swift = (ROOT / "Culvo" / "Updates.swift").read_text()
releases = re.findall(r'Release\(version: "([^"]+)", name: "([^"]+)", highlights: \[(.*?)\]\)', updates_swift, re.S)
blocks = []
for i, (version, name, body) in enumerate(releases):
    items = re.findall(r'"((?:[^"\\]|\\.)*)"', body)
    current = ' <span class="tag">Current</span>' if i == 0 else ""
    blocks.append(f"<h2>{html.escape(name)}</h2>\n<p class=\"ver\">Version {html.escape(version)}{current}</p>\n<ul>"
                  + "".join(f"<li>{html.escape(t)}</li>" for t in items) + "</ul>")
(SITE / "updates").mkdir(exist_ok=True)
(SITE / "updates" / "index.html").write_text(PAGE.format(
    title="What's new",
    body='<p>Every Culvo version, newest first.</p>\n' + "\n".join(blocks),
    extra='<style>ul { color: var(--muted); padding-left: 20px; } li { margin: 6px 0; } .ver { font-size: 14px; } '
          '.tag { background: var(--lime); color: #0B0B0C; border-radius: 99px; padding: 2px 8px; font-weight: 700; font-size: 12px; margin-left: 6px; }</style>',
    company=values["company"], company_details=html.escape(values["companyDetails"]), updated=updated))

(SITE / "index.html").write_text(
    '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=https://culvo.app">'
    '<title>Culvo</title><a href="https://culvo.app">culvo.app</a>\n')
print("Built privacy/, terms/, refunds/, cookies/, accessibility/, support/ and updates/")
