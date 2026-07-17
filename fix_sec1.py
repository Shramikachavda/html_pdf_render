import re

with open("/home/shramikachavda/html_pdf_render/sec_1.txt", "r") as f:
    text = f.read()

# Replace all "\s+(1\.\d+.*?)\s+" with newlines
text = re.sub(r' (1\.\d+ )', r'\n\n\1', text)
text = text.replace(" 1. Executive Summary", "1. Executive Summary")

with open("/home/shramikachavda/html_pdf_render/sec_1.txt", "w") as f:
    f.write(text.strip() + "\n")
