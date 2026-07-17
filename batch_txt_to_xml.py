import os
import re

txt_files = [
    ("sec_1.txt", "sec_1.xml", "EXECUTIVE SUMMARY", "INTRODUCTION", True),
    ("sec_2_3_4.txt", "sec_2_3_4.xml", "ARCHITECTURE &amp; WORKFLOW", "ARCHITECTURE", False),
    ("sec_5.txt", "sec_5.xml", "SYSTEM ARCHITECTURE", "ARCHITECTURE", True),
    ("sec_6.txt", "sec_6.xml", "TECHNOLOGY STACK", "TECHNOLOGY", True),
    ("sec_7.txt", "sec_7.xml", "API DESIGN", "API", True),
    ("sec_8.txt", "sec_8.xml", "FRONTEND INTEGRATION", "FRONTEND", True),
    ("sec_9_10_11.txt", "sec_9_10_11.xml", "DATA &amp; DEPLOYMENT", "INFRASTRUCTURE", True),
    ("sec_12.txt", "sec_12.xml", "CONCLUSION", "SUMMARY", True),
    ("sec_13.txt", "sec_13.xml", "RISKS &amp; LIMITATIONS", "RISK MANAGEMENT", True),
    ("SEC_14.TXT", "SEC_14.xml", "FUTURE ENHANCEMENTS", "ROADMAP", False),
    ("gradrails.txt", "gradrails.xml", "AI GUARDRAILS STRATEGY", "AI GUARDRAILS", True)
]

def parse_markdown_table(lines, i):
    table_lines = []
    while i < len(lines) and lines[i].strip().startswith('|'):
        table_lines.append(lines[i].strip())
        i += 1
    
    xml_out = ["    <table>"]
    for idx, row in enumerate(table_lines):
        # Skip separator row
        if re.match(r'^\|[-\s|:]+\|$', row):
            continue
        cells = [c.strip() for c in row.split('|')[1:-1]]
        
        row_str = f'      <row header="1">' if idx == 0 else '      <row>'
        for cell in cells:
            # Handle inline bolding
            cell = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cell)
            cell = re.sub(r'\*(.*?)\*', r'<i>\1</i>', cell)
            # escape ampersands
            cell = cell.replace("&", "&amp;")
            row_str += f'<cell>{cell}</cell>'
        row_str += '</row>'
        xml_out.append(row_str)
    
    xml_out.append("    </table>")
    return xml_out, i

def convert_txt_to_xml(in_file, out_file, label, kicker, use_unformatted_headers):
    if not os.path.exists(in_file):
        return
        
    with open(in_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out = ['<?xml version="1.0" encoding="UTF-8"?>', f'<doc title="{label}">']
    
    sheet_count = 0
    in_sheet = False
    in_list = False
    in_code = False
    
    def open_sheet(title=None):
        nonlocal sheet_count, in_sheet
        if in_sheet:
            out.append('  </sheet>\n')
        sheet_count += 1
        out.append(f'  <!-- ============ SHEET {sheet_count:02d} ============ -->')
        title_attr = f' title="{title.replace("&", "&amp;")}"' if title else ""
        out.append(f'  <sheet label="{label}" kicker="{kicker}" footnum="{sheet_count:02d}"{title_attr}>')
        in_sheet = True

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        if line.startswith("```"):
            if not in_code:
                in_code = True
                out.append('    <pre>')
            else:
                in_code = False
                out.append('    </pre>')
            i += 1
            continue
            
        if in_code:
            out.append('    ' + line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            i += 1
            continue

        if not line:
            if in_list:
                out.append('    </ul>')
                in_list = False
            i += 1
            continue
            
        if line.startswith('|'):
            if in_list:
                out.append('    </ul>')
                in_list = False
            table_xml, i = parse_markdown_table(lines, i)
            out.extend(table_xml)
            continue
            
        # Headings
        m_h1 = re.match(r'^#\s+(.*)', line)
        m_h2 = re.match(r'^##\s+(.*)', line)
        m_h3 = re.match(r'^###\s+(.*)', line)
        
        # Unformatted number headers
        if not (m_h1 or m_h2 or m_h3) and use_unformatted_headers:
            if re.match(r'^\d+\.\s+[A-Za-z]', line):
                m_h2 = re.match(r'^(\d+\.\s+.*)', line)
            elif re.match(r'^\d+\.\d+\s+[A-Za-z]', line):
                m_h3 = re.match(r'^(\d+\.\d+\s+.*)', line)
        
        if m_h1 or m_h2:
            if in_list:
                out.append('    </ul>')
                in_list = False
            title = m_h1.group(1) if m_h1 else m_h2.group(1)
            open_sheet(title)
            escaped_title = title.replace("&", "&amp;")
            out.append(f'    <h2>{escaped_title}</h2>')
            i += 1
            continue
            
        if m_h3:
            if in_list:
                out.append('    </ul>')
                in_list = False
            escaped_h3 = m_h3.group(1).replace("&", "&amp;")
            out.append(f'    <h3>{escaped_h3}</h3>')
            i += 1
            continue
            
        # Lists
        m_li = re.match(r'^-\s+(.*)', line)
        if m_li:
            if not in_list:
                out.append('    <ul>')
                in_list = True
            content = m_li.group(1)
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f'      <li>{content}</li>')
            i += 1
            continue
            
        # Blockquote / Callout
        m_bq = re.match(r'^>\s*(.*)', line)
        if m_bq:
            if in_list:
                out.append('    </ul>')
                in_list = False
            content = m_bq.group(1)
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            out.append(f'    <callout>{content}</callout>')
            i += 1
            continue
            
        # Paragraphs
        if not in_sheet:
            open_sheet(label)
            
        if in_list:
            out.append('    </ul>')
            in_list = False
            
        # format bolding
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append(f'    <p>{line}</p>')
        i += 1

    if in_list:
        out.append('    </ul>')
    if in_sheet:
        out.append('  </sheet>')
        
    out.append('</doc>')
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

for in_f, out_f, label, kicker, unformatted in txt_files:
    convert_txt_to_xml(in_f, out_f, label, kicker, unformatted)
    print(f"Rebuilt {out_f}")

