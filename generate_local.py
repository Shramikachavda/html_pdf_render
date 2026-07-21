import os

diagrams = {
    "{{DIAGRAM_WORKFLOW}}": "dia_1.svg",
    "{{DIAGRAM_SEQUENCE}}": "mermaid-diagram (4).png",
    "{{DIAGRAM_COMPONENTS}}": "dia_2.svg",
    "{{DIAGRAM_GUARDRAIL}}": "mermaid-diagram (5).png",
    "{{DIAGRAM_FALLBACK}}": "mermaid-diagram (6).png"
}

with open("new_html.html", "r", encoding="utf-8") as f:
    html_content = f.read()

for placeholder, img_filename in diagrams.items():
    img_tag = f'<div class="diagram-box"><img src="{img_filename}" style="width:100%; max-width:800px; display:block; margin:auto;" /></div>'
    html_content = html_content.replace(placeholder, img_tag)

with open("final_output_local.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated final_output_local.html")
