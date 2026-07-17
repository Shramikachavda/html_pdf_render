import os
import re

sections = [
    ("sec_1.xml", "01", "Executive Summary", "Project overview and goals"),
    ("sec_2_3_4.xml", "02", "Overall Approach", "System workflow and pipelines"),
    ("sec_5.xml", "03", "System Architecture", "Backend systems and orchestration"),
    ("sec_6.xml", "04", "Technology Stack &amp; Design Decisions", "Tools, frameworks, and rationale"),
    ("gradrails.xml", "05", "AI Guardrails Strategy", "Safety and scoping constraints"),
    ("sec_7.xml", "06", "API Design &amp; Communication Flow", "Endpoints and data models"),
    ("sec_8.xml", "07", "Frontend Integration", "User experience and widgets"),
    ("sec_9_10_11.xml", "08", "Data Handling &amp; Deployment", "Operations, security, and roll-out"),
    ("sec_12.xml", "09", "Monitoring &amp; Logging", "System observability"),
    ("sec_13.xml", "10", "Risks &amp; Limitations", "Security assessment and mitigation"),
    ("SEC_14.xml", "11", "Future Enhancements", "Project roadmap"),
    ("conclusion", "12", "Conclusion", "Final thoughts"),
    ("appendics.xml", "13", "Appendices", "ADRs, Guardrails, and Testing"),
    ("req_question.xml", "14", "Requirement Gathering Questions", "Project scope definition")
]

base_dir = "/home/shramikachavda/html_pdf_render"
output_file = "final_content.xml"

conclusion_xml = """
  <!-- ============ SHEET 01 ============ -->
  <sheet label="CONCLUSION" kicker="CONCLUSION" title="12. Conclusion" footnum="01">
    <h2>12.1 Final Thoughts</h2>
    <p>The Theta Chat Bot represents a significant step forward in providing immediate, accurate, and context-aware assistance to website visitors. By leveraging a Retrieval-Augmented Generation (RAG) architecture grounded in official company data, the chatbot ensures high reliability while mitigating the risks of hallucinations and unsupported responses.</p>
    <p>With its modular design, robust guardrails, and flexible deployment options, the system is well-positioned to scale with Theta Technolabs' future requirements, ultimately improving user engagement and reducing the support workload.</p>
  </sheet>
"""

with open(os.path.join(base_dir, output_file), "w", encoding="utf-8") as out:
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.write('<doc title="Theta ChatBot Technical Documentation">\n')
    out.write('  <cover kicker="TECHNICAL DESIGN DOCUMENT" title="Theta Chat Bot" subtitle="Architecture, Implementation &amp; Guardrails Strategy" image="image_transparent.png" />\n')
    out.write('  <toc title="Contents">\n')
    
    for fname, num, title, desc in sections:
        out.write(f'    <item n="{num}" title="{title}" desc="{desc}" />\n')
        
    out.write('  </toc>\n\n')

    for fname, num, title, desc in sections:
        if fname == "conclusion":
            out.write(f'  <!-- ======================= conclusion ======================= -->\n')
            out.write(conclusion_xml.strip() + '\n\n')
            continue

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
            
            out.write(f'  <!-- ======================= {fname} ======================= -->\n')
            out.write(content.strip() + '\n\n')

    out.write('</doc>\n')

print(f"Successfully created {output_file}")
