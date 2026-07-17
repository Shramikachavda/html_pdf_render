import os

def insert_img_after(file_path, target_text, img_file):
    if not os.path.exists(file_path): return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    img_tag = f'\n    <raw><img src="{img_file}" style="width:100%; max-width:800px; display:block; margin:auto;" /></raw>\n'
    
    if target_text in content and img_tag not in content:
        content = content.replace(target_text, target_text + img_tag, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path} with {img_file}")

base = "/home/shramikachavda/html_pdf_render"

# SVGs
insert_img_after(os.path.join(base, "sec_2_3_4.xml"), "<h3>2.3 System Workflow</h3>", "dia_1.svg")
insert_img_after(os.path.join(base, "sec_2_3_4.xml"), "<h3>3.9 Knowledge Lifecycle</h3>", "dia_3.svg")
insert_img_after(os.path.join(base, "sec_5.xml"), "<h3>5.10 Component Communication</h3>", "dia_2.svg")

# PNGs
insert_img_after(os.path.join(base, "sec_6.xml"), "<h2>3.2 Technology Stack Overview</h2>", "mermaid-diagram (4).png")
insert_img_after(os.path.join(base, "sec_7.xml"), "<h3>7.1 Overview</h3>", "mermaid-diagram (5).png")
insert_img_after(os.path.join(base, "sec_8.xml"), "<h3>8.1 Overview</h3>", "mermaid-diagram (6).png")
insert_img_after(os.path.join(base, "sec_9_10_11.xml"), "<h3>9.1 Overview</h3>", "mermaid-diagram (7).png")
