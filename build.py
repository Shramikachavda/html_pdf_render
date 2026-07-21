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
@page {
  size: A4;
  margin: 25mm 20mm 25mm 20mm;
  @bottom-right {
    content: "PAGE " counter(page);
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 8pt;
    color: #6b7a86;
  }
  @bottom-left {
    content: string(doctitle, first);
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 8pt;
    color: #6b7a86;
  }
}
@page:first {
  margin: 0;
  @bottom-right { content: normal; }
  @bottom-left { content: normal; }
}
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "DejaVu Sans", Arial, sans-serif; color: #16232f; font-size: 10.1pt; line-height: 1.52; background: #fff; overflow-wrap: break-word; word-wrap: break-word; }
img, pre, table { max-width: 100%; }
svg { max-width: 100%; }
.mermaid.fixed-height svg { width: 100%; height: 100%; }
.mono { font-family: "DejaVu Sans Mono", monospace; }
.chapter { page-break-after: always; }
.cover { background:#0d2b45; color:#e8f1f6; padding:0; box-sizing: border-box; height: 297mm; page-break-after: always; }
.cover .kicker2 { font-family:"DejaVu Sans Mono",monospace; color:#bfe3ef; letter-spacing:4px; font-size:9.5pt; margin-bottom:10mm; text-transform: uppercase; font-weight: bold; }
.cover h1 { font-size:36pt; color:#ffffff; line-height:1.15; margin-bottom:6mm; border-bottom:none; font-weight: 800; letter-spacing: -1px; }
.cover .subtitle { font-size:14pt; color:#bfe3ef; max-width:135mm; margin-bottom:40mm; font-weight: 500; }
table.revtable { width:100%; border-collapse:collapse; margin-top:4mm; font-family:"DejaVu Sans Mono",monospace; font-size:8.5pt; }
table.revtable th, table.revtable td { border:0.5pt solid rgba(255, 255, 255, 0.15); padding:2.5mm 3mm; color:#cfe4ee; text-align:left; }
table.revtable th { background:rgba(0, 0, 0, 0.15); color:#7fd0e6; letter-spacing:1px; font-weight:bold; }
tr { page-break-inside: avoid; }
table { page-break-inside: avoid; break-inside: avoid; }
h1, h2, h3, h4, h5, h6 { page-break-after: avoid; break-after: avoid; }
.kicker { font-family:"DejaVu Sans Mono",monospace; font-size:8pt; letter-spacing:2.5px; color:#1c5d8c; font-weight:bold; margin-bottom:2mm; }
h1.section-title { font-size:20pt; color:#0d2b45; border-bottom:2pt solid #0d2b45; padding-bottom:3mm; margin-bottom:6mm; string-set: doctitle content(); }
h2 { font-size:12.5pt; color:#0d2b45; margin-top:6.5mm; margin-bottom:3mm; padding-left:3mm; border-left:3pt solid #e8a33d; }
h3 { font-size:10.3pt; color:#1c5d8c; margin-top:4.5mm; margin-bottom:2mm; font-family:"DejaVu Sans Mono",monospace; letter-spacing:0.5px; }
p { margin-bottom:2.8mm; text-align:justify; }
ul, ol { margin:2mm 0 3mm 5mm; padding-left: 5mm; }
li { margin-bottom:1.4mm; }
strong { color:#0d2b45; }
table.spec { width:100%; border-collapse:collapse; margin:3mm 0 5mm 0; font-size:8.8pt; }
table.spec th { background:#0d2b45; color:#fff; text-align:left; padding:2.1mm 3mm; font-family:"DejaVu Sans Mono",monospace; font-size:7.8pt; letter-spacing:0.5px; }
table.spec td { padding:2.1mm 3mm; border-bottom:0.5pt solid #d8dfe4; vertical-align:top; }
table.spec tr:nth-child(even) td { background:#f4f7f9; }
table.spec td .mono { font-family:"DejaVu Sans Mono",monospace; font-size:8.1pt; color:#1c5d8c; }
.callout { background:#f4f7f9; border-left:3pt solid #1c5d8c; padding:3mm 4mm; margin:4mm 0; font-size:9.1pt; page-break-inside: avoid; }
.callout .lbl { font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; letter-spacing:2px; color:#1c5d8c; font-weight:bold; display:block; margin-bottom:1.5mm; }
.decision { background:#fdf6ea; border-left:3pt solid #e8a33d; padding:3mm 4mm; margin:4mm 0; font-size:9.1pt; page-break-inside: avoid; }
.decision .lbl { font-family:"DejaVu Sans Mono",monospace; font-size:7.5pt; letter-spacing:2px; color:#b5791c; font-weight:bold; display:block; margin-bottom:1.5mm; }
.tag { display:inline-block; font-family:"DejaVu Sans Mono",monospace; font-size:7.3pt; letter-spacing:1px; color:#1c5d8c; background:#f4f7f9; border:0.5pt solid #1c5d8c; padding:0.6mm 2mm; border-radius:3px; margin-right:1.6mm; margin-bottom:1.5mm; }
.tag-danger { color:#7f1d1d; background:#fef2f2; border:0.5pt solid #fecaca; }
.mermaid { background-color:#f8fafc; padding:5mm; border-radius:3px; border:0.5pt solid #e2e8f0; margin:5mm 0; text-align:center; page-break-inside: avoid; display: flex; justify-content: center; white-space: pre-wrap; font-family: inherit; zoom: 0.75; }
pre.mermaid svg { max-height: 155mm !important; max-width: 100% !important; height: auto !important; width: auto !important; }
.steps { margin:3mm 0; }
.step { position:relative; padding:2mm 0 2mm 11mm; border-bottom:0.4pt dotted #c7d2da; page-break-inside: avoid; }
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

.toc-row { display:block; padding:2mm 0; border-bottom:0.4pt dotted #c7d2da; page-break-inside: avoid; }
.toc-row .tn { font-family:"DejaVu Sans Mono",monospace; color:#1c5d8c; font-weight:bold; display:inline-block; width:12mm; }
.toc-row .tt { font-size:10.2pt; color:#0d2b45; font-weight:bold; }
.toc-row .td { font-size:8.4pt; color:#6b7a86; display:block; margin-left:12mm; }
svg { display:block; margin:3mm auto; }
.json-block { margin: 4mm 0; page-break-inside: avoid; border-radius: 4px; border: 0.6pt solid #d8dfe4; background: #fafcff; overflow: hidden; }
.json-block.error { border-color: #fecaca; background: #fffcfc; }
.json-block .jhead { padding: 2.5mm 4mm; display: block; overflow: hidden; }
.json-block:not(.error) .jhead { background: #0d2b45; color: #fff; border-bottom: 0.6pt solid #0d2b45; }
.json-block.error .jhead { background: #ed5f5f; color: #fff; border-bottom: 0.6pt solid #ed5f5f; }
.json-block .jlabel { font-family: "DejaVu Sans Mono", monospace; font-weight: bold; font-size: 8pt; letter-spacing: 1px; float: left; text-transform: uppercase; }
.json-block:not(.error) .jlabel { color: #e8a33d; }
.json-block.error .jlabel { color: #fff; }
.json-block .badge { float: right; font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; opacity: 0.8; }
.json-block .jbody { padding: 4mm; font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; color: #5a6b7c; }
.json-block .jrow { margin: 1mm 0; }
.json-block .jkey { font-weight: bold; }
.json-block:not(.error) .jkey { color: #1c5d8c; }
.json-block.error .jkey { color: #dc2626; }
.json-block .jval { color: #40a070; }
.json-block .jnote { border-top: 0.6pt solid #d8dfe4; padding: 2mm 4mm; font-size: 7.5pt; color: #8292a1; background: #f4f7f9; }
.json-block.error .jnote { border-top-color: #fecaca; color: #d64a4a; background: #fdf3f3; }
"""

INLINE_TAG_MAP = {
    "b": "strong",
    "strong": "strong",
    "i": "em",
    "em": "em",
    "code": "span class=\"mono\"",
    "mono": "span class=\"mono\"",
    "p": "p",
    "br": "br",
    "hlt": "span class=\"tag tag-danger\"",
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
        if tag == "br":
            parts.append("<br>")
        elif tag == "link":
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
    tag_type = tags_el.get("type", "")
    tag_class = "tag tag-danger" if tag_type == "danger" else "tag"
    pills = "".join(f'<span class="{tag_class}">{esc(t.text)}</span>' for t in tags_el.findall("tag"))
    return f"<p>{pills}</p>"


def render_callout(el, css_class):
    label = el.get("label", "")
    body = inline_html(el)
    lbl_html = f'<span class="lbl">{esc(label)}</span>' if label else ""
    return f'<div class="{css_class}">{lbl_html}{body}</div>'


def render_list(el, tag):
    items = "".join(f"<li>{inline_html(li)}</li>" for li in el.findall("item"))
    return f"<{tag}>{items}</{tag}>"


def render_adr(el):
    title = esc(el.get("title", ""))
    
    decision_el = el.find("decision")
    decision_text = inline_html(decision_el) if decision_el is not None else ""
    
    alternatives_el = el.find("alternatives")
    alternatives_html = ""
    if alternatives_el is not None:
        items = "".join(f"<li>{inline_html(li)}</li>" for li in alternatives_el.findall("item"))
        alternatives_html = f"<ul>{items}</ul>"
        
    rationale_el = el.find("rationale")
    rationale_text = inline_html(rationale_el) if rationale_el is not None else ""
    
    impact_el = el.find("impact")
    impact_html = ""
    if impact_el is not None:
        pos = esc(impact_el.get("pos", ""))
        neg = esc(impact_el.get("neg", ""))
        pos_html = f'<span class="impact-pos">Positive:</span> {pos}<br>' if pos else ""
        neg_html = f'<span class="impact-neg">Trade-off:</span> {neg}' if neg else ""
        impact_html = f"{pos_html}{neg_html}"
        
    return f"""
    <div class="adr">
      <div class="adr-head">{title}</div>
      <div class="adr-body">
        <div class="adr-row"><span class="k">DECISION</span>{decision_text}</div>
        <div class="adr-row"><span class="k">ALTERNATIVES CONSIDERED</span>{alternatives_html}</div>
        <div class="adr-row"><span class="k">RATIONALE</span>{rationale_text}</div>
        <div class="adr-row"><span class="k">IMPACT</span>{impact_html}</div>
      </div>
    </div>
    """

def render_why(el):
    """Renders the <why> tag as an info callout."""
    icon = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-2px; margin: 0 5px 0 0;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    return f'<div class="callout"><span class="lbl">{icon}WHY THIS IS ASKED</span>{inline_html(el)}</div>'

def render_json_block(el):
    type_attr = esc(el.get("type", ""))
    label = esc(el.get("label", ""))
    badge = esc(el.get("badge", ""))
    note = esc(el.get("note", ""))
    
    jfields = el.findall("jfield")
    rows = []
    for i, jfield in enumerate(jfields):
        key = esc(jfield.get("key", ""))
        val = esc(jfield.get("val", ""))
        comma = "," if i < len(jfields) - 1 else ""
        rows.append(f'<div class="jrow">&nbsp;&nbsp;<span class="jkey">"{key}"</span>: <span class="jval">"{val}"</span>{comma}</div>')
    
    body = '<div>{</div>\n' + "\n".join(rows) + '\n<div>}</div>'
    
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    header_html = f'<div class="jhead"><span class="jlabel">{label}</span>{badge_html}</div>'
    
    note_html = ""
    if note:
        note_html = f'<div class="jnote"><span style="margin-right:2px; display:inline-block; transform:translateY(1px);">&#9432;</span> {note}</div>'
        
    return f'<div class="json-block {type_attr}">{header_html}<div class="jbody">{body}</div>{note_html}</div>'

def render_block(el):
    """Dispatch one block-level XML element to its HTML rendering."""
    t = el.tag
    if t == "h2":
        return f"<h2>{inline_html(el)}</h2>"
    if t == "h3":
        return f"<h3>{inline_html(el)}</h3>"
    if t == "json-block":
        return render_json_block(el)
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
    if t == "adr":
        return render_adr(el)
    if t == "why":
        return render_why(el)
    if t == "svg":
        import xml.etree.ElementTree as ET
        return ET.tostring(el, encoding="utf-8").decode("utf-8")
    if t == "raw":
        return (el.text or "").strip()
    if t == "mermaid-diagram":
        diagram_code = (el.text or "").strip()
        height = el.get("height")
        width = el.get("width")
        
        style = "text-align:center; margin: 20px 0;"
        cls = "mermaid"
        if height:
            style += f" height: {height};"
            cls += " fixed-height"
        if width:
            style += f" width: {width};"
            
        return f'<div class="{cls}" style="{style}">\n{diagram_code}\n</div>'
    return ""


def render_sheet(sheet_el, doc_title):
    kicker = esc(sheet_el.get("kicker", ""))
    title = esc(sheet_el.get("title", ""))
    body_html = "".join(render_block(child) for child in sheet_el)
    kicker_html = f'<div class="kicker">{kicker}</div>' if kicker else ""
    return f"""
<div class="chapter">
  {kicker_html}
  <h1 class="section-title">{title}</h1>
  {body_html}
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
    
    img_html = f'<div style="text-align:left; margin-bottom: 25mm;"><img src="{image}" style="max-width:280px;" /></div>' if image else ""
    
    return f"""
<div class="cover">
  <div style="padding: 40mm 20mm;">
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
    heading = esc(toc_el.get("title", "Contents"))
    return f"""
<div class="chapter">
  <div class="kicker">DOCUMENT INDEX</div>
  <h1 class="section-title">{heading}</h1>
  {''.join(rows)}
</div>
"""


def build_docs(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()  # <doc>
    doc_title = root.get("title", "Untitled Document")

    cover_parts = []
    content_parts = []
    for child in root:
        if child.tag == "cover":
            cover_parts.append(render_cover(child, doc_title))
        elif child.tag == "toc":
            content_parts.append(render_toc(child, doc_title))
        elif child.tag == "sheet":
            content_parts.append(render_sheet(child, doc_title))

    final_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{esc(doc_title)}</title>
<style>{CSS}</style>
</head>
<body>
{''.join(cover_parts)}
{''.join(content_parts)}

<script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
    startOnLoad: true,
    fontFamily: '"DejaVu Sans", Arial, sans-serif',
    flowchart: {{ htmlLabels: false }},
    themeVariables: {{
        fontFamily: '"DejaVu Sans", Arial, sans-serif'
    }}
}});
</script>
</body></html>"""

    return final_html


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 build.py content.xml output.pdf")
        sys.exit(1)
    xml_path, pdf_path = sys.argv[1], sys.argv[2]
    base_name = pdf_path.rsplit(".", 1)[0]
    html_path = base_name + ".html"

    final_html = build_docs(xml_path)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"Wrote intermediate HTML file: {html_path}")

    from playwright.sync_api import sync_playwright
    import os
    import urllib.parse

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Using a standard viewport; Mermaid scales SVGs to 100% max-width anyway.
        page = browser.new_page()
        
        file_url = "file://" + urllib.parse.quote(os.path.abspath(html_path))
        page.goto(file_url, wait_until="networkidle")
        
        # Wait for all mermaid diagrams to be processed
        page.wait_for_function('() => document.querySelectorAll(".mermaid:not([data-processed=\\"true\\"])").length === 0')
        
        rendered_html = page.content()
        browser.close()
        
    rendered_path = base_name + "_rendered.html"
    with open(rendered_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    print(f"Wrote fully rendered HTML to {rendered_path}")
    
    result = subprocess.run(
        [
            "weasyprint", rendered_path, pdf_path
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("weasyprint failed:")
        print(result.stderr)
        sys.exit(1)

    print(f"Wrote {pdf_path}")

if __name__ == "__main__":
    main()