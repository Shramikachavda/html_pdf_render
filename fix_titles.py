import re
import glob

def fix():
    pattern = re.compile(r'<p style="text-align:center;"><b>(Figure .*?)</b></p>')
    files = glob.glob("*.xml")
    for f in files:
        if f == "final_content.xml":
            continue
        with open(f, 'r') as file:
            content = file.read()
        
        new_content = pattern.sub(r'<p align="center" style="text-align: center !important; color: #555555 !important;"><b>\1</b></p>', content)
        
        if new_content != content:
            with open(f, 'w') as file:
                file.write(new_content)
            print(f"Updated {f}")

if __name__ == "__main__":
    fix()
