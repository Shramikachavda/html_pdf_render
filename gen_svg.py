import os
import base64
import requests

files = ['dia_1', 'dia_2', 'dia_3']
base_dir = '/home/shramikachavda/html_pdf_render'

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as infile:
            mermaid_text = infile.read()
        
        # mermaid.ink requires base64 encoding without padding optionally, but standard base64 url-safe is better
        # Actually mermaid.ink uses base64 string
        graphbytes = mermaid_text.encode("utf8")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = f"https://mermaid.ink/svg/{base64_string}"
        
        response = requests.get(url)
        if response.status_code == 200:
            out_path = os.path.join(base_dir, f + ".svg")
            with open(out_path, 'w', encoding='utf-8') as outfile:
                outfile.write(response.text)
            print(f"Successfully generated {f}.svg")
        else:
            print(f"Failed to generate {f}.svg, status: {response.status_code}")
