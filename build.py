#!/usr/bin/env python3
"""
build.py — turn a simple XML file into a styled, paginated PDF.

Usage:
    python3 build.py content.xml output.pdf

No LLM calls. No internet. Just Python's built-in XML parser + wkhtmltopdf
(already installed in this environment). Re-run any time your content changes.

See TAGS.md for the full list of tags and what each one does.
"""
import sys
import subprocess
import xml.etree.ElementTree as ET

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "DejaVu Sans", Arial, sans-serif; color: #16232f; font-size: 10.1pt; line-height: 1.52; background: #fff; }
.mono { font-family: "DejaVu Sans Mono", monospace; }
.sheet { position: relative; width: 210mm; min-height: 297mm; padding: 20mm 16mm 16mm 16mm; page-break-after: always; }
.sheet:last-child { page-break-after: auto; }
.rail { position: absolute; top:0; left:0; bottom:0; width:9mm; background:#0d2b45; }
.rail-label { position:absolute; top:50%; left:-38mm; width:90mm; transform:rotate(-90deg); transform-origin:left top;
  color:#bfe3ef; font-family:"DejaVu Sans Mono",monospace; font-size:8pt; letter-spacing:3px; text-align:left; }
.sheet-body { margin-left:9mm; padding-left:9mm; }
.sheet-foot { position:absolute; bottom:8mm; left:18mm; right:16mm; border-top:0.5pt solid #c7d2da; padding-top:3mm;
  font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; color:#6b7a86; }
.sheet-foot .num { float:right; }
.cover { background:#0d2b45; color:#e8f1f6; padding:0; }
.cover-inner { padding:26mm 18mm; }
.cover .kicker2 { font-family:"DejaVu Sans Mono",monospace; color:#6ec6dd; letter-spacing:4px; font-size:9.5pt; margin-bottom:10mm; }
.cover h1 { font-size:32pt; line-height:1.15; margin-bottom:6mm; border-bottom:none; }
.cover .subtitle { font-size:11.5pt; color:#9fc3d6; max-width:135mm; margin-bottom:50mm; }
table.revtable { width:100%; border-collapse:collapse; margin-top:4mm; font-family:"DejaVu Sans Mono",monospace; font-size:8pt; }
table.revtable th, table.revtable td { border:0.5pt solid #2f5674; padding:2mm 2.5mm; color:#cfe4ee; text-align:left; }
table.revtable th { background:#123a5c; color:#7fd0e6; letter-spacing:1px; }
.kicker { font-family:"DejaVu Sans Mono",monospace; font-size:8pt; letter-spacing:2.5px; color:#1c5d8c; font-weight:bold; margin-bottom:2mm; }
h1.section-title { font-size:20pt; color:#0d2b45; border-bottom:2pt solid #0d2b45; padding-bottom:3mm; margin-bottom:6mm; }
h2 { font-size:12.5pt; color:#0d2b45; margin-top:6.5mm; margin-bottom:3mm; padding-left:3mm; border-left:3pt solid #e8a33d; }
h3 { font-size:10.3pt; color:#1c5d8c; margin-top:4.5mm; margin-bottom:2mm; font-family:"DejaVu Sans Mono",monospace; letter-spacing:0.5px; }
p { margin-bottom:2.8mm; text-align:justify; }
ul, ol { margin:2mm 0 3mm 5mm; }
li { margin-bottom:1.4mm; }
strong { color:#0d2b45; }
table.spec { width:100%; border-collapse:collapse; margin:3mm 0 5mm 0; font-size:8.8pt; }
table.spec th { background:#0d2b45; color:#fff; text-align:left; padding:2.1mm 3mm; font-family:"DejaVu Sans Mono",monospace; font-size:7.8pt; letter-spacing:0.5px; }
table.spec td { padding:2.1mm 3mm; border-bottom:0.5pt solid #d8dfe4; vertical-align:top; }
table.spec tr:nth-child(even) td { background:#f4f7f9; }
table.spec td .mono { font-family:"DejaVu Sans Mono",monospace; font-size:8.1pt; color:#1c5d8c; }
.callout { background:#f4f7f9; border-left:3pt solid #1c5d8c; padding:3mm 4mm; margin:4mm 0; font-size:9.1pt; }
.callout .lbl { font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; letter-spacing:2px; color:#1c5d8c; font-weight:bold; display:block; margin-bottom:1.5mm; }
.decision { background:#fdf6ea; border-left:3pt solid #e8a33d; padding:3mm 4mm; margin:4mm 0; font-size:9.1pt; }
.decision .lbl { font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; letter-spacing:2px; color:#b5791c; font-weight:bold; display:block; margin-bottom:1.5mm; }
.tag { display:inline-block; font-family:"DejaVu Sans Mono",monospace; font-size:7.3pt; letter-spacing:1px; color:#fff; background:#1c5d8c; padding:0.7mm 2mm; border-radius:2px; margin-right:1.6mm; }
.steps { margin:3mm 0; }
.step { position:relative; padding:2mm 0 2mm 11mm; border-bottom:0.4pt dotted #c7d2da; }
.step:last-child { border-bottom:none; }
.step .n { position:absolute; left:0; top:2mm; width:7mm; height:7mm; background:#0d2b45; color:#bfe3ef;
  font-family:"DejaVu Sans Mono",monospace; font-size:8pt; font-weight:bold; text-align:center; line-height:7mm; }
.step .t { font-weight:bold; color:#0d2b45; font-size:9.3pt; }
.step .d { font-size:8.8pt; color:#3a4954; }

.adr { border: 0.6pt solid #d8dfe4; margin: 4mm 0 6mm 0; page-break-inside: avoid; }
.adr-head { background: #0d2b45; color: #bfe3ef; font-family: "DejaVu Sans Mono", monospace; font-size: 9.5pt; font-weight: bold; padding: 2.5mm 4mm; letter-spacing: 0.5px; }
.adr-body { padding: 3mm 4mm; font-size: 9pt; }
.adr-row { margin-bottom: 2.5mm; }
.adr-row .k { font-family: "DejaVu Sans Mono", monospace; font-size: 7.8pt; letter-spacing: 1px; color: #1c5d8c; font-weight: bold; display: block; margin-bottom: 0.8mm; }
.adr-row ul { margin: 1mm 0 0 4.5mm; }
.impact-pos { color: #1c7c4d; }
.impact-neg { color: #b5791c; }

.toc-row { display:block; padding:2mm 0; border-bottom:0.4pt dotted #c7d2da; }
.toc-row .tn { font-family:"DejaVu Sans Mono",monospace; color:#1c5d8c; font-weight:bold; display:inline-block; width:12mm; }
.toc-row .tt { font-size:10.2pt; color:#0d2b45; font-weight:bold; }
.toc-row .td { font-size:8.4pt; color:#6b7a86; display:block; margin-left:12mm; }
svg { display:block; margin:3mm auto; }
"""

INLINE_TAG_MAP = {
    "b": "strong",
    "strong": "strong",
    "i": "em",
    "em": "em",
    "code": "span class=\"mono\"",
    "mono": "span class=\"mono\"",
}


def esc(text):
    if text is None:
        return ""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def inline_html(elem):
    """Render an element's mixed text/child content to inline HTML.
    Supports <b>/<strong>, <i>/<em>, <code>/<mono>, <link href="...">."""
    parts = [esc(elem.text)]
    for child in elem:
        inner = inline_html(child)
        tag = child.tag
        if tag == "link":
            href = esc(child.get("href", "#"))
            parts.append(f'<a href="{href}">{inner}</a>')
        elif tag in INLINE_TAG_MAP:
            open_tag = INLINE_TAG_MAP[tag]
            close_tag = open_tag.split()[0]
            parts.append(f"<{open_tag}>{inner}</{close_tag}>")
        else:
            parts.append(inner)
        parts.append(esc(child.tail))
    return "".join(parts)


def render_table(tbl):
    rows_html = []
    for row in tbl.findall("row"):
        is_header = row.get("header") == "1"
        cell_tag = "th" if is_header else "td"
        cells = []
        for cell in row.findall("cell"):
            content = inline_html(cell)
            if cell.get("mono") == "1" and not is_header:
                content = f'<span class="mono">{content}</span>'
            width = cell.get("width")
            style = f' style="width:{width}"' if width else ""
            cells.append(f"<{cell_tag}{style}>{content}</{cell_tag}>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")
    return f'<table class="spec">{"".join(rows_html)}</table>'


def render_steps(steps_el):
    out = ['<div class="steps">']
    for i, step in enumerate(steps_el.findall("step"), start=1):
        title = esc(step.get("title", ""))
        desc = inline_html(step)
        out.append(
            f'<div class="step"><span class="n">{i}</span>'
            f'<span class="t">{title}</span><span class="d">{desc}</span></div>'
        )
    out.append("</div>")
    return "".join(out)


def render_tags(tags_el):
    pills = "".join(f'<span class="tag">{esc(t.text)}</span>' for t in tags_el.findall("tag"))
    return f"<p>{pills}</p>"


def render_callout(el, css_class):
    label = el.get("label", "")
    body = inline_html(el)
    lbl_html = f'<span class="lbl">{esc(label)}</span>' if label else ""
    return f'<div class="{css_class}">{lbl_html}{body}</div>'


def render_list(el, tag):
    items = "".join(f"<li>{inline_html(li)}</li>" for li in el.findall("item"))
    return f"<{tag}>{items}</{tag}>"


def render_block(el):
    """Dispatch one block-level XML element to its HTML rendering."""
    t = el.tag
    if t == "h2":
        return f"<h2>{inline_html(el)}</h2>"
    if t == "h3":
        return f"<h3>{inline_html(el)}</h3>"
    if t == "p":
        return f"<p>{inline_html(el)}</p>"
    if t == "table":
        return render_table(el)
    if t == "callout":
        return render_callout(el, "callout")
    if t == "decision":
        return render_callout(el, "decision")
    if t == "steps":
        return render_steps(el)
    if t == "tags":
        return render_tags(el)
    if t == "list":
        return render_list(el, "ul")
    if t == "orderedlist":
        return render_list(el, "ol")
    if t == "svg":
        # raw passthrough — write inline SVG markup directly inside a <raw> child,
        # or just place raw SVG text as the element's text content.
        return (el.text or "").strip()
    if t == "raw":
        return (el.text or "").strip()
    return ""


def render_sheet(sheet_el, doc_title):
    label = esc(sheet_el.get("label", doc_title))
    kicker = esc(sheet_el.get("kicker", ""))
    title = esc(sheet_el.get("title", ""))
    footnum = esc(sheet_el.get("footnum", ""))
    body_html = "".join(render_block(child) for child in sheet_el)
    kicker_html = f'<div class="kicker">{kicker}</div>' if kicker else ""
    return f"""
<div class="sheet">
  <div class="rail"><div class="rail-label mono">{label}</div></div>
  <div class="sheet-body">
    {kicker_html}
    <h1 class="section-title">{title}</h1>
    {body_html}
  </div>
  <div class="sheet-foot"><span>{esc(doc_title)}</span><span class="num">SHEET {footnum}</span></div>
</div>
"""


def render_cover(cover_el, doc_title):
    kicker = esc(cover_el.get("kicker", ""))
    title = esc(cover_el.get("title", doc_title))
    subtitle = esc(cover_el.get("subtitle", ""))
    image = cover_el.get("image")
    fields = cover_el.findall("field")
    rows = "".join(
        f"<tr><td>{esc(f.get('name',''))}</td><td>{inline_html(f)}</td></tr>" for f in fields
    )
    table_html = f'<table class="revtable"><tr><th>Field</th><th>Value</th></tr>{rows}</table>' if fields else ""
    
    img_html = f'<div style="text-align:center; margin-bottom: 20mm;"><img src="{image}" style="max-width:200px;" /></div>' if image else ""
    
    return f"""
<div class="sheet cover">
  <div class="cover-inner">
    {img_html}
    <div class="kicker2">{kicker}</div>
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
    {table_html}
  </div>
</div>
"""


def render_toc(toc_el, doc_title):
    rows = []
    for item in toc_el.findall("item"):
        n = esc(item.get("n", ""))
        title = esc(item.get("title", ""))
        desc = esc(item.get("desc", ""))
        rows.append(
            f'<span class="toc-row"><span class="tn">{n}</span>'
            f'<span class="tt">{title}</span><span class="td">{desc}</span></span>'
        )
    label = esc(toc_el.get("label", doc_title))
    heading = esc(toc_el.get("title", "Contents"))
    return f"""
<div class="sheet">
  <div class="rail"><div class="rail-label mono">{label}</div></div>
  <div class="sheet-body">
    <div class="kicker">SHEET INDEX</div>
    <h1 class="section-title">{heading}</h1>
    {''.join(rows)}
  </div>
  <div class="sheet-foot"><span>{esc(doc_title)}</span><span class="num">SHEET 00</span></div>
</div>
"""


def build_html(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()  # <doc>
    doc_title = root.get("title", "Untitled Document")

    body_parts = []
    for child in root:
        if child.tag == "cover":
            body_parts.append(render_cover(child, doc_title))
        elif child.tag == "toc":
            body_parts.append(render_toc(child, doc_title))
        elif child.tag == "sheet":
            body_parts.append(render_sheet(child, doc_title))

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{esc(doc_title)}</title>
<style>{CSS}</style></head>
<body>
{''.join(body_parts)}
</body></html>"""
    return html


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 build.py content.xml output.pdf")
        sys.exit(1)
    xml_path, pdf_path = sys.argv[1], sys.argv[2]
    html_path = pdf_path.rsplit(".", 1)[0] + ".html"

    html = build_html(xml_path)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {html_path}")

    result = subprocess.run(
        ["wkhtmltopdf", "--enable-local-file-access", "--quiet", html_path, pdf_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("wkhtmltopdf failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()