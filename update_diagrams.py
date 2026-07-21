import os
import re

xml_files = [f for f in os.listdir('.') if f.endswith('.xml') and f != 'final_content.xml']

# We will just print some context around mermaid diagrams to see what they are about
for file in xml_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.finditer(r'<mermaid-diagram>', content)
    for match in matches:
        start = max(0, match.start() - 200)
        end = min(len(content), match.start() + 200)
        print(f"--- {file} ---")
        print(content[start:end])
