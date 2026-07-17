import os
import re
import base64
import requests

def update_mermaid_style(file_name):
    path = os.path.join("/home/shramikachavda/html_pdf_render", file_name)
    if not os.path.exists(path): return
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define our theme strings
    THEME_PRIMARY = "fill:#f4f7f9,stroke:#1c5d8c,stroke-width:2px,color:#0d2b45"
    THEME_ACCENT = "fill:#fdf6ea,stroke:#e8a33d,stroke-width:2px,color:#b5791c"
    THEME_DARK = "fill:#0d2b45,stroke:#2f5674,stroke-width:2px,color:#cfe4ee"
    THEME_MID = "fill:#123a5c,stroke:#7fd0e6,stroke-width:2px,color:#ffffff"
    
    # We will just replace style lines based on what they represent
    # This is a bit brute force but works for these 3 files.
    new_lines = []
    for line in content.split("\n"):
        if line.startswith("style "):
            target = line.split(" ")[1]
            # Map targets to themes
            if target in ["USER", "FRONTEND", "A", "C", "D"]:
                line = f"style {target} {THEME_PRIMARY}"
            elif target in ["BACKEND", "AI", "RAG", "ORCH", "B", "E", "F"]:
                line = f"style {target} {THEME_ACCENT}"
            elif target in ["KNOWLEDGE", "STORAGE", "VECTOR", "DB", "I", "H", "INFRA"]:
                line = f"style {target} {THEME_DARK}"
            else:
                line = f"style {target} {THEME_MID}"
                
        new_lines.append(line)
        
    updated_content = "\n".join(new_lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    # Re-generate SVG
    graphbytes = updated_content.encode("utf8")
    base64_string = base64.b64encode(graphbytes).decode("ascii")
    url = f"https://mermaid.ink/svg/{base64_string}"
    
    response = requests.get(url)
    if response.status_code == 200:
        svg_path = path + ".svg"
        with open(svg_path, 'w', encoding='utf-8') as outfile:
            outfile.write(response.text)
        print(f"Updated style and regenerated {file_name}.svg")
    else:
        print(f"Failed to regenerate {file_name}.svg")

update_mermaid_style("dia_1")
update_mermaid_style("dia_2")
update_mermaid_style("dia_3")
