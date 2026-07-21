import re
import urllib.parse
import os
import subprocess
from playwright.sync_api import sync_playwright

def get_mermaid_from_xml(filename, figure_title):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract height attribute if exists
    pattern = r'<mermaid-diagram([^>]*)>(.*?)</mermaid-diagram>\s*<p[^>]*><b>Figure [^:]+: ([^<]+)</b></p>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for attrs, diagram, title in matches:
        if figure_title.lower() in title.lower():
            height_match = re.search(r'height="([^"]+)"', attrs)
            height = height_match.group(1) if height_match else None
            return diagram.strip(), height
    return None, None

diagram_mapping = {
    "{{DIAGRAM_WORKFLOW}}": ("final_content.xml", "System Workflow"),
    "{{DIAGRAM_SYNC_WORKFLOW}}": ("final_content.xml", "Synchronization Workflow"),
    "{{DIAGRAM_KNOWLEDGE_LIFECYCLE}}": ("final_content.xml", "Knowledge Lifecycle"),
    "{{DIAGRAM_SEQUENCE}}": ("final_content.xml", "Request Processing Sequence"),
    "{{DIAGRAM_PROMPT_FLOW}}": ("final_content.xml", "Prompt Assembly Flow"),
    "{{DIAGRAM_E2E_HANDLING}}": ("final_content.xml", "End-to-End Query Handling"),
    "{{DIAGRAM_COMPONENTS}}": ("final_content.xml", "Component Communication"),
    "{{DIAGRAM_COMP_INTERACTION}}": ("final_content.xml", "Component Interaction Architecture"),
    "{{DIAGRAM_API_ARCH}}": ("final_content.xml", "API Communication Architecture"),
    "{{DIAGRAM_FRONTEND_INTEGRATION}}": ("final_content.xml", "Frontend Integration Overview"),
    "{{DIAGRAM_FRONTEND_REQUEST_FLOW}}": ("final_content.xml", "Frontend Request Flow"),
    "{{DIAGRAM_GUARDRAIL}}": ("final_content.xml", "Guardrail Workflow"),
    "{{DIAGRAM_FALLBACK_STRATEGY}}": ("final_content.xml", "Fallback Strategy Decision Process"),
    "{{DIAGRAM_DASHBOARD}}": ("final_content.xml", "Dashboard Architecture Overview"),
    "{{DIAGRAM_MONITORING}}": ("final_content.xml", "Monitoring and Observability Strategy"),
    "{{DIAGRAM_FALLBACK}}": ("final_content.xml", "Frontend Request Flow") # For backward compatibility just in case
}

with open("new_html.html", 'r', encoding='utf-8') as f:
    html_content = f.read()

# Add A4 and Mermaid CSS if not present
extra_css = """
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
    content: "Theta ChatBot Technical Design";
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
.mermaid { background-color:#f8fafc; padding:5mm; border-radius:3px; border:0.5pt solid #e2e8f0; margin:5mm 0; text-align:center; page-break-inside: avoid; display: flex; justify-content: center; font-family: inherit; zoom: 0.75; }
pre.mermaid svg { max-height: 155mm !important; max-width: 100% !important; height: auto !important; width: auto !important; }
.mermaid.fixed-height svg { width: 100%; height: 100%; }
"""

if "@page" not in html_content:
    html_content = html_content.replace("<style>", "<style>\n" + extra_css)

for placeholder, (xml_file, figure_name) in diagram_mapping.items():
    diagram_code, height = get_mermaid_from_xml(xml_file, figure_name)
    if diagram_code:
        style = "text-align:center; margin: 20px 0;"
        cls = "mermaid"
        if height:
            style += f" height: {height};"
            cls += " fixed-height"
        mermaid_html = f'<div class="{cls}" style="{style}">\n{diagram_code}\n</div>'
        html_content = html_content.replace(placeholder, mermaid_html)
        print(f"Replaced {placeholder} with diagram: {figure_name} (Height: {height})")
    else:
        print(f"Could not find diagram for {placeholder} ({figure_name})")

image_html = """
<div style="text-align:center; margin: 25px 0;">
<img src="chatbot_placement.png" style="max-height: 90mm; width: auto;" />
<div style="text-align:center; font-size: 8.5pt; font-weight: bold; color: #1c5d8c; margin-top: 8px;">Figure 8.2: Chatbot Widget Placement Options</div>
</div>
"""
html_content = html_content.replace("{{IMAGE_CHATBOT}}", image_html)

mermaid_script = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
    startOnLoad: true,
    fontFamily: '"DejaVu Sans", Arial, sans-serif',
    flowchart: { htmlLabels: false },
    themeVariables: {
        fontFamily: '"DejaVu Sans", Arial, sans-serif'
    }
});
</script>
"""
if "mermaid.min.js" not in html_content:
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", mermaid_script + "</body>")
    else:
        html_content += mermaid_script

with open("final_with_mermaid_a4.html", 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Rendering with playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    file_url = "file://" + urllib.parse.quote(os.path.abspath("final_with_mermaid_a4.html"))
    page.goto(file_url, wait_until="networkidle")
    
    try:
        page.wait_for_function('() => document.querySelectorAll(".mermaid:not([data-processed=\\"true\\"])").length === 0', timeout=10000)
    except Exception as e:
        print("Timeout waiting for mermaid, continuing anyway...", e)
        
    rendered_html = page.content()
    browser.close()

with open("final_rendered_mermaid_a4.html", 'w', encoding='utf-8') as f:
    f.write(rendered_html)

print("Generating PDF with weasyprint...")
subprocess.run(["weasyprint", "final_rendered_mermaid_a4.html", "Theta_ChatBot_Technical_Design.pdf"])
print("PDF Generation complete: Theta_ChatBot_Technical_Design.pdf")
