import os

def insert_img_after(file_path, target_text, img_file):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    img_tag = f'\n    <raw><img src="{img_file}" style="width:100%; max-width:800px; display:block; margin:auto;" /></raw>\n'
    
    if target_text in content and img_tag not in content:
        content = content.replace(target_text, target_text + img_tag, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")

base = "/home/shramikachavda/html_pdf_render"
insert_img_after(os.path.join(base, "sec_6.xml"), "<h2>3.1 Introduction</h2>", "mermaid-diagram (4).png")
insert_img_after(os.path.join(base, "sec_7.xml"), "<h2>7.1 Overview</h2>", "mermaid-diagram (5).png")
insert_img_after(os.path.join(base, "sec_8.xml"), "<h2>8.1 Overview</h2>", "mermaid-diagram (6).png")
insert_img_after(os.path.join(base, "sec_9_10_11.xml"), "<h2>9.1 Overview</h2>", "mermaid-diagram (7).png")
