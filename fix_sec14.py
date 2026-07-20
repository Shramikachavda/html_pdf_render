import re

with open("SEC_14.xml", "r") as f:
    content = f.read()

# Extract the header and the very first sheet opening
header = """<?xml version="1.0" encoding="UTF-8"?>
<doc title="FUTURE ENHANCEMENTS">
  <!-- ============ SHEET 01 ============ -->
  <sheet label="FUTURE ENHANCEMENTS" kicker="ROADMAP" footnum="01" title="15. Future Roadmap">"""

# Remove all sheet boundaries and footers
body = content
# Remove everything before the first <h2>15. Future Roadmap</h2>
body = body[body.find("<h2>15. Future Roadmap</h2>"):]
# Remove all </sheet>
body = body.replace("</sheet>", "")
# Remove all </doc>
body = body.replace("</doc>", "")
# Remove all <sheet ...> lines
body = re.sub(r'<sheet.*?>\n', '', body)
# Remove all <!-- ==== SHEET ... ==== --> lines
body = re.sub(r'\s*<!-- ============ SHEET \d+ ============ -->\n', '', body)
# Remove horizontal lines `<p>---</p>`
body = body.replace("<p>---</p>", "")

# Clean up multiple newlines
body = re.sub(r'\n{3,}', '\n\n', body).strip()

final_content = f"{header}\n    {body}\n  </sheet>\n</doc>\n"

with open("SEC_14.xml", "w") as f:
    f.write(final_content)
