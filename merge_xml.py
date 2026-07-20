import os
import re

files_in_order = [
    "sec_1.xml",
    "sec_2_3_4.xml",
    "sec_5.xml",
    "sec_6.xml",
    "gradrails.xml",
    "sec_7.xml",
    "sec_8.xml",
    "sec_9_10_11.xml",
    "sec_12.xml",
    "sec_13.xml",
    "SEC_14.xml",
    "req_question.xml"
]

output_file = "final_content.xml"
base_dir = "/home/shramikachavda/html_pdf_render"

with open(os.path.join(base_dir, output_file), "w", encoding="utf-8") as out:
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<doc title="Theta ChatBot Technical Documentation">\n')
    out.write('  <cover image="Screenshot_from_2026-07-17_19-25-42-removebg-preview.png" kicker="TECHNICAL DESIGN DOCUMENT" title="Theta Chat Bot" subtitle="Comprehensive Architecture, API, and AI Guardrails Strategy">\n')
    out.write('    <field name="Project Name">Theta Chat Bot</field>\n')
    out.write('    <field name="Prepared For">Theta Technolabs Internal Engineering</field>\n')
    out.write('    <field name="Author">Shramika Chavda</field>\n')
    out.write('    <field name="Document Version">1.0 </field>\n')
    out.write('    <field name="Date">July 2026</field>\n')
    out.write('  </cover>\n')
    
    # We could dynamically generate the TOC, but for now let's just append the sheets.
    # The frontend renderer usually creates the TOC based on <sheet title="..."> if needed, 
    # or we can leave out the <toc> block if the format doesn't strictly require it.
    # We will add a basic TOC.
    out.write('  <toc title="Contents">\n')
    out.write('    <item n="01" title="Executive Summary" desc="Overview and goals" />\n')
    out.write('    <item n="02" title="Pipelines: Solution Overview" desc="Core architecture" />\n')
    out.write('    <item n="03" title="Knowledge Management Pipeline" desc="Data ingestion" />\n')
    out.write('    <item n="04" title="Retrieval &amp; Response Generation" desc="RAG processing" />\n')
    out.write('    <item n="05" title="System Architecture" desc="Backend systems" />\n')
    out.write('    <item n="06" title="Technology Stack" desc="Tools and languages" />\n')
    out.write('    <item n="07" title="API Design &amp; Communication Flow" desc="Endpoints and data models" />\n')
    out.write('    <item n="08" title="Frontend Integration" desc="User experience and widgets" />\n')
    out.write('    <item n="09" title="Operations &amp; AI Guardrails" desc="Dashboard &amp; AI Safety" />\n')
    out.write('    <item n="10" title="Security &amp; Bot Prevention" desc="CAPTCHA and rate limiting" />\n')
    out.write('    <item n="11" title="Deployment Strategy" desc="Infrastructure rollout" />\n')
    out.write('    <item n="12" title="Monitoring &amp; Logging" desc="Observability" />\n')
    out.write('    <item n="13" title="Risk Assessment &amp; Mitigation" desc="Security and risks" />\n')
    out.write('    <item n="14" title="Future Roadmap" desc="Next steps" />\n')
    out.write('    <item n="15" title="Requirement Gathering Questions" desc="Project scope definition" />\n')
    out.write('  </toc>\n\n')

    sheet_counter = [1]
    def replace_footnum(match):
        res = f'footnum="{sheet_counter[0]:02d}"'
        sheet_counter[0] += 1
        return res

    for fname in files_in_order:
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            print(f"Warning: {fname} not found.")
            continue
            
        with open(fpath, "r", encoding="utf-8") as infile:
            content = infile.read()
            
            # Remove XML declaration
            content = re.sub(r'<\?xml.*?\?>', '', content)
            
            # Remove <doc ...> and </doc>
            content = re.sub(r'<doc[^>]*>', '', content)
            content = content.replace('</doc>', '')
            
            # Sequentially number sheets page-wise across the entire document
            content = re.sub(r'footnum="\d+"', replace_footnum, content)
            
            out.write(f'  <!-- ======================= {fname} ======================= -->\n')
            out.write(content.strip() + '\n\n')

    out.write('</doc>\n')

print(f"Successfully created {output_file}")
