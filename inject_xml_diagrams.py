import re
import urllib.parse
import os
import subprocess
from playwright.sync_api import sync_playwright

def get_mermaid_from_xml(filename, figure_title):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid diagrams and their following captions
    pattern = r'<mermaid-diagram[^>]*>(.*?)</mermaid-diagram>\s*<p[^>]*><b>Figure [^:]+: ([^<]+)</b></p>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for diagram, title in matches:
        if figure_title.lower() in title.lower():
            return diagram.strip()
    return None

diagram_mapping = {
    "{{DIAGRAM_WORKFLOW}}": ("final_content.xml", "System Workflow"),
    "{{DIAGRAM_SEQUENCE}}": ("final_content.xml", "Request Processing Sequence"),
    "{{DIAGRAM_COMPONENTS}}": ("final_content.xml", "Component Communication"),
    "{{DIAGRAM_GUARDRAIL}}": ("final_content.xml", "Guardrail Workflow"),
    "{{DIAGRAM_FALLBACK}}": ("final_content.xml", "Frontend Request Flow") # Fallback to Frontend Flow? Or maybe there's a specific fallback one
}

# If Fallback doesn't exist, we will try to find "Synchronization Workflow" or something else
with open("new_html.html", 'r', encoding='utf-8') as f:
    html_content = f.read()

for placeholder, (xml_file, figure_name) in diagram_mapping.items():
    diagram_code = get_mermaid_from_xml(xml_file, figure_name)
    if diagram_code:
        # We put it in a div with class "mermaid"
        mermaid_html = f'<div class="mermaid" style="text-align:center; margin: 20px 0;">\n{diagram_code}\n</div>'
        html_content = html_content.replace(placeholder, mermaid_html)
        print(f"Replaced {placeholder} with diagram: {figure_name}")
    else:
        print(f"Could not find diagram for {placeholder} ({figure_name})")

# Add mermaid JS script to the HTML before closing body tag, if it's not already there
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

with open("final_with_mermaid.html", 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Rendering with playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    file_url = "file://" + urllib.parse.quote(os.path.abspath("final_with_mermaid.html"))
    page.goto(file_url, wait_until="networkidle")
    
    # Wait for mermaid to process all diagrams
    try:
        page.wait_for_function('() => document.querySelectorAll(".mermaid:not([data-processed=\\"true\\"])").length === 0', timeout=10000)
    except Exception as e:
        print("Timeout waiting for mermaid, continuing anyway...", e)
        
    rendered_html = page.content()
    browser.close()

with open("final_rendered_mermaid.html", 'w', encoding='utf-8') as f:
    f.write(rendered_html)

print("Generating PDF with weasyprint...")
subprocess.run(["weasyprint", "final_rendered_mermaid.html", "Theta_ChatBot_Technical_Design.pdf"])
print("PDF Generation complete: Theta_ChatBot_Technical_Design.pdf")
